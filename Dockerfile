# 使用 miniconda3 作为基础镜像，方便安装生物信息学工具
FROM continuumio/miniconda3:latest

# 设置元数据
LABEL maintainer="qww"
LABEL description="Docker environment for BioAnalyze Toolkit"

# 设置环境变量
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 设置时区和系统依赖
# 安装中文字体以支持 bio-analyze-plot 的中文显示
# 增加 libgl1 和 libglib2.0-0 用于 pymol 等图形库支持
# 注意：在 Debian Bookworm/Trixie 中，libgl1-mesa-glx 已被 libgl1 替代
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    procps \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 配置 Conda 频道
RUN conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority strict

# Step 1: Install Python and Build Tools
RUN conda install -y \
    python=3.11 \
    conda-build \
    anaconda-client \
    matplotlib \
    seaborn \
    scikit-learn \
    pandas \
    numpy \
    scipy \
    openpyxl \
    && conda clean -afy

# Step 2: Install Bio-informatics Tools (Heavy dependencies)
RUN conda install -y \
    fastp \
    salmon \
    fastqc \
    star \
    samtools \
    gffread \
    sra-tools \
    pdbfixer \
    vina \
    meeko \
    propka \
    openbabel \
    rdkit \
    pymol-open-source \
    gemmi \
    && conda clean -afy

# 安装 uv (已移除，改用 conda 本地构建)
# RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装项目包到系统环境 (Conda)
# 使用 conda build 和 install --use-local 安装本地包
# 按依赖顺序构建和安装
RUN conda build conda_recipes/bio-analyze-core -c conda-forge -c bioconda && \
    conda install --use-local bio-analyze-core && \
    conda build conda_recipes/bio-analyze-plot -c conda-forge -c bioconda && \
    conda install --use-local bio-analyze-plot && \
    conda build conda_recipes/bio-analyze-docking -c conda-forge -c bioconda && \
    conda install --use-local bio-analyze-docking && \
    conda build conda_recipes/bio-analyze-rna-seq -c conda-forge -c bioconda && \
    conda install --use-local bio-analyze-rna-seq && \
    conda build conda_recipes/bio-analyze-cli -c conda-forge -c bioconda && \
    conda install --use-local bio-analyze-cli && \
    conda install pytest pytest-cov && \
    conda clean -afy

# 默认命令
ENTRYPOINT ["bioanalyze"]
CMD ["--help"]
