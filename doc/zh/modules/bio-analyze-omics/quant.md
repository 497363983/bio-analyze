---
---

# quant

使用可扩展的插件式框架进行转录本或基因表达定量。

当前已接入的后端包括：

- `salmon`
- `kallisto`
- `featurecounts`
- `htseq-count`
- `rsem`

该框架统一了：

- 工具选择与依赖检查
- 参考文件准备与转录组 FASTA 提取
- 参数模板与阶段化参数追加
- 标准输出格式（`counts.csv`、指标矩阵、结果清单）
- 多工具交叉验证与比较分析输出

## 命令行用法

**命令**: `quant`

### 关键参数

<ParamTable params-path="omics/rna_seq_quant_cli" />

### 示例

```bash
uv run bioanalyze omics rna_seq quant \
  -i ./clean_data \
  -o ./quant_results \
  --fasta genome.fa \
  --gtf genes.gtf \
  --tool salmon \
  --compare-tool kallisto
```

## 架构说明

### 核心组件

- `QuantManager`: 量化编排层，负责选择主量化工具、执行可选比较工具并写出标准化结果
- `BaseQuantifier`: 构建在 `bio_analyze_core.engine.BaseEngine` 之上的量化专用引擎接口
- `QuantifierRegistry`: 由 `bio_analyze_core.engine.EngineRegistry` 支撑的兼容注册表门面
- `QuantRunResult`: 统一结果对象，封装计数矩阵、指标矩阵、样本输出、元数据和清单文件

### 与共享 Engine 框架的集成

- 量化引擎现已注册到共享的 `bio_analyze.engine` entry-point group
- 领域名称固定为 `quant`
- 当前引擎名包括 `salmon`、`kallisto`、`featurecounts`、`htseq-count` 和 `rsem`
- `QuantManager` 内部通过 `bio_analyze_core.engine.EngineManager` 完成引擎创建与动态切换

### 标准输出布局

- `counts.csv`: 主量化结果的标准计数矩阵，供 DE 模块继续使用
- `result_manifest.json`: 工具、样本输出和元数据摘要
- `tpm.csv`、`length.csv` 等指标矩阵（视后端而定）
- `comparisons/<tool>/...`: 比较工具的标准化输出
- `tool_comparison.csv`: 开启比较工具时输出跨工具 Pearson 相关性表

### 后端模式

- 基于 reads 的定量：`salmon`、`kallisto`、`rsem`
- 基于比对结果的定量：`featurecounts`、`htseq-count`

对于基于 BAM 的工具，管理器会优先尝试复用同级 `align/` 目录下的标准 STAR 输出。

## Python API

### 主量化流程

```python
from pathlib import Path

from bio_analyze_omics.rna_seq.quant import QuantManager

reads = {
    "sample1": {"R1": Path("sample1_1.fq.gz"), "R2": Path("sample1_2.fq.gz")},
    "sample2": {"R1": Path("sample2_1.fq.gz"), "R2": Path("sample2_2.fq.gz")},
}
reference = {
    "fasta": Path("genome.fa"),
    "gtf": Path("genes.gtf")
}

manager = QuantManager(
    reads=reads,
    reference=reference,
    output_dir=Path("./quant_results"),
    threads=8,
    tool="salmon",
    compare_tools=["kallisto"],
    tool_config={
        "template": "default",
        "sample_workers": 2,
        "phases": {"quant": ["--seqBias", "--gcBias"]},
    },
)

counts_df = manager.run()
comparison_df = manager.get_comparison_table()
```

### 可用工具发现

```python
from bio_analyze_omics.rna_seq.quant import list_available_quantifiers

print(list_available_quantifiers())
```

## 配置模型

`run` 命令可从配置文件读取 `quant` 段：

```yaml
quant:
  tool: salmon
  compare_tools:
    - kallisto
  primary:
    template: default
    sample_workers: 2
    phases:
      quant:
        - --seqBias
        - --gcBias
  compare:
    kallisto:
      template: bootstrap
      phases:
        quant:
          - -b
          - "50"
```

### 模板语义

- `template`: 选择后端预置模板
- `phases.index`: 追加到索引/参考构建命令的参数
- `phases.quant`: 追加到定量命令的参数
- `sample_workers`: 样本级并行执行的工作线程数
- `params`: 结构化工具参数，例如 `library_type`、`fragment_length`、`fragment_sd`

## 扩展指南

新增一个定量工具时，推荐按以下步骤接入：

1. 继承 `BaseQuantifier`
2. 定义 `TOOL_NAME`、`MODE` 和 `REQUIRED_BINARIES`
3. 实现 `execute()` 及可选的 `build_index()`、`quantify_sample()` 等辅助方法
4. 返回 `QuantRunResult`
5. 使用 `@register_quantifier` 完成注册
6. 添加命令构建、结果解析、标准化输出的单元测试

最小示例：

```python
from bio_analyze_omics.rna_seq.quant import (
    BaseQuantifier,
    QuantRunResult,
    register_quantifier,
)


@register_quantifier
class MyQuantifier(BaseQuantifier):
    TOOL_NAME = "mytool"
    MODE = "reads"
    REQUIRED_BINARIES = ("mytool",)

    def execute(self) -> QuantRunResult:
        counts = ...
        return QuantRunResult(
            tool=self.TOOL_NAME,
            output_dir=self.output_dir,
            counts_matrix=counts,
        )
```

## 测试策略

- 单元测试：
  - 验证每个量化后端的命令构建、依赖检查、模板展开和结果解析
  - 对外部二进制统一使用 mock，避免依赖本地真实安装环境
  - 校验标准化输出文件，例如 `counts.csv`、指标矩阵和 `result_manifest.json`
- 集成测试：
  - 覆盖 `QuantManager` 主工具加比较工具的组合运行流程
  - 验证基于比对结果的工具能够复用 `align/` 目录中的 BAM
  - 确认跨工具比较结果会写出到 `tool_comparison.csv`
- 回归重点：
  - 保护断点续跑、不完整索引重建、压缩注释恢复和配置加载等关键路径
  - 仅在能降低互操作风险或解析歧义时增加后端专属测试

## 说明

- Salmon 与 Kallisto 适合转录本层面的丰度估计，并可输出 TPM 等指标矩阵。
- FeatureCounts 与 HTSeq-count 使用比对 BAM 和注释文件进行基因层计数。
- 对于 Salmon 的 mapping-based 模式，建议优先准备 decoy-aware transcriptome 以提升准确性。
