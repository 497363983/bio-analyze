import shutil
import subprocess
import json
from pathlib import Path
from collections import defaultdict

from bio_analyze_core.logging import get_logger
from bio_analyze_core.subprocess import run as run_command

logger = get_logger(__name__)

class QCManager:
    def __init__(self, input_dir: Path, output_dir: Path, threads: int = 4, skip_qc: bool = False, skip_trim: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.threads = threads
        self.skip_qc = skip_qc
        self.skip_trim = skip_trim
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> dict[str, dict]:
        """
        运行 QC 和修剪。
        返回一个映射 sample_name -> {"R1": path, "R2": path} 的字典
        """
        if self.skip_qc and self.skip_trim:
            logger.info("Skipping QC and Trimming steps.")
            return self._detect_files(self.input_dir)

        # 首先检测文件
        samples = self._detect_files(self.input_dir)
        cleaned_samples = {}
        
        for sample, files in samples.items():
            logger.info(f"Processing sample: {sample}")
            
            # 构建输出路径
            r1_out = self.output_dir / f"{sample}_clean_R1.fastq.gz"
            r2_out = None
            if "R2" in files:
                r2_out = self.output_dir / f"{sample}_clean_R2.fastq.gz"
            
            json_report = self.output_dir / f"{sample}_fastp.json"
            html_report = self.output_dir / f"{sample}_fastp.html"
            
            # FastQC 逻辑 (可选)
            fastqc_out_dir = self.output_dir / "fastqc"
            fastqc_out_dir.mkdir(exist_ok=True)
            
            if shutil.which("fastqc"):
                qc_cmd = ["fastqc", "-o", str(fastqc_out_dir), "-t", str(self.threads), str(files["R1"])]
                if "R2" in files:
                    qc_cmd.append(str(files["R2"]))
                    
                try:
                    run_command(qc_cmd, check=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"FastQC failed for sample {sample}: {e}")
                    # 不抛出异常，只记录日志，因为修剪可能仍然有效
            else:
                logger.warning("FastQC not found. Skipping FastQC report generation. Using fastp for QC.")

            # 仍然运行 fastp 进行修剪和基本 QC
            if json_report.exists() and html_report.exists():
                logger.info(f"QC reports for {sample} already exist. Skipping.")
                cleaned_samples[sample] = {"R1": r1_out}
                if r2_out:
                    cleaned_samples[sample]["R2"] = r2_out
                continue

            # 构建 fastp 命令
            cmd = [
                "fastp",
                "-i", str(files["R1"]),
                "-o", str(r1_out),
                "-j", str(json_report),
                "-h", str(html_report),
                "-w", str(self.threads)
            ]
            
            if "R2" in files:
                cmd.extend(["-I", str(files["R2"]), "-O", str(r2_out)])
            
            if self.skip_trim:
                # 禁用修剪但仍输出文件和 QC 报告
                cmd.extend(["--disable_adapter_trimming", "--disable_trim_poly_g", "--disable_quality_filtering"])
            
            # 运行 fastp
            try:
                run_command(cmd, check=True)
                
                cleaned_samples[sample] = {"R1": r1_out}
                if r2_out:
                    cleaned_samples[sample]["R2"] = r2_out
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"fastp failed for sample {sample}: {e}")
                raise

        return cleaned_samples

    def _detect_files(self, directory: Path) -> dict[str, dict]:
        """
        检测双端或单端 FastQ 文件。
        返回: {sample_name: {"R1": path, "R2": path}}
        """
        files = sorted(list(directory.glob("*.fastq.gz")) + list(directory.glob("*.fq.gz")))
        samples = defaultdict(dict)
        
        for f in files:
            name = f.name
            # R1/R2 的简单启发式规则
            if "_R1" in name or "_1." in name:
                # 移除扩展名逻辑
                sample_name = name.split("_R1")[0].split("_1.")[0]
                samples[sample_name]["R1"] = f
            elif "_R2" in name or "_2." in name:
                sample_name = name.split("_R2")[0].split("_2.")[0]
                samples[sample_name]["R2"] = f
            else:
                # 单端?
                sample_name = name.split(".")[0]
                samples[sample_name]["R1"] = f
        
        return dict(samples)

    def get_stats(self) -> dict:
        # 如果可用，解析 FastQC 报告以获取统计信息，否则回退到 fastp
        stats = {}
        
        # 尝试首先解析 fastp json，因为它有现成的 clean read 计数
        for json_file in self.output_dir.glob("*_fastp.json"):
            sample = json_file.stem.replace("_fastp", "")
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    summary = data.get("summary", {})
                    before = summary.get("before_filtering", {})
                    after = summary.get("after_filtering", {})
                    
                    stats[sample] = {
                        "total_reads": before.get("total_reads", 0),
                        "clean_reads": after.get("total_reads", 0),
                        "q30_rate": f"{before.get('q30_rate', 0) * 100:.2f}",
                        "mapping_rate": "N/A"
                    }
            except Exception as e:
                logger.warning(f"Failed to parse fastp report for {sample}: {e}")
        
        # 在完整的 FastQC 实现中，我们会在这里解析 FastQC 的 zip/html 输出
        # 但如果不使用 MultiQC，通过编程解析 FastQC 输出比较困难。
        # 由于我们仍然运行 fastp 进行修剪，使用它的统计信息更方便。
        
        return stats
