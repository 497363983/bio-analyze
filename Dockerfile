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
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 配置 Conda 频道
RUN conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority strict

# 安装生物信息学工具
# fastp: 质控和修剪
# salmon: 定量
# fastqc: 质量报告
# gffread: 基因组工具
# python=3.11: 指定 Python 版本
RUN conda install -y \
    python=3.11 \
    fastp \
    salmon \
    fastqc \
    gffread \
    && conda clean -afy

# 安装 uv
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 创建虚拟环境并安装项目包
# 使用 editable 模式安装，方便开发和调试（如果是用于生产，可以构建 wheel）
# 这里的顺序不重要，uv 会解析依赖，但显式列出所有包
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install \
    -e packages/core \
    -e packages/plot \
    -e packages/rna_seq \
    -e packages/docking \
    -e packages/cli

# 设置 PATH，确保可以直接调用 bio-cli
ENV PATH="/app/.venv/bin:$PATH"

# 默认命令
ENTRYPOINT ["bio-cli"]
CMD ["--help"]
