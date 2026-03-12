#!/bin/bash

# bio-analyse 环境搭建脚本
# 适用于 Linux 和 macOS (包括 Windows WSL)

set -e

# 定义颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   Bio-Analyze Environment Setup Script   ${NC}"
echo -e "${GREEN}==========================================${NC}"

# 1. 检查 Conda/Mamba
echo -e "\n${YELLOW}[1/5] Checking for Conda/Mamba...${NC}"
if command -v mamba &> /dev/null; then
    CONDA_EXE=mamba
    echo -e "${GREEN}Found Mamba at $(command -v mamba).${NC}"
elif command -v conda &> /dev/null; then
    CONDA_EXE=conda
    echo -e "${GREEN}Found Conda at $(command -v conda).${NC}"
else
    echo -e "${RED}Error: Conda or Mamba is not installed.${NC}"
    echo "Please install Miniconda or Mambaforge first:"
    echo "  Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    echo "  Mambaforge: https://github.com/conda-forge/miniforge"
    exit 1
fi

# 2. 配置 Conda Channels
echo -e "\n${YELLOW}[2/5] Configuring Conda channels...${NC}"
$CONDA_EXE config --add channels defaults
$CONDA_EXE config --add channels bioconda
$CONDA_EXE config --add channels conda-forge
$CONDA_EXE config --set channel_priority strict
echo -e "${GREEN}Channels configured.${NC}"

# 3. 创建 Conda 环境
ENV_NAME="bio_analyse_env"
echo -e "\n${YELLOW}[3/5] Creating/Updating environment: $ENV_NAME...${NC}"

if $CONDA_EXE info --envs | grep -q "$ENV_NAME"; then
    echo -e "${GREEN}Environment $ENV_NAME already exists.${NC}"
else
    echo -e "Creating new environment with Python 3.11..."
    $CONDA_EXE create -n $ENV_NAME -y python=3.11
fi

# 4. 安装生物信息学工具
echo -e "\n${YELLOW}[4/5] Installing bioinformatics tools...${NC}"
echo "Installing: fastp, salmon, fastqc, star, samtools, gffread, sra-tools, uv"

# 注意：某些工具在 macOS (ARM64) 上可能不可用，或者需要特定的 channel 配置
# 这里假设用户在 x86_64 Linux 或通过 Rosetta 运行
$CONDA_EXE install -n $ENV_NAME -y \
    fastp \
    salmon \
    fastqc \
    star \
    samtools \
    gffread \
    sra-tools \
    uv

# 5. 安装 bio-analyse 包
echo -e "\n${YELLOW}[5/5] Installing bio-analyse packages...${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 使用环境中的 uv 安装项目包
# -e (editable) 模式允许用户修改源码后立即生效
echo "Installing packages from $SCRIPT_DIR/packages/..."

$CONDA_EXE run -n $ENV_NAME uv pip install -e "$SCRIPT_DIR/packages/core"
$CONDA_EXE run -n $ENV_NAME uv pip install -e "$SCRIPT_DIR/packages/plot"
$CONDA_EXE run -n $ENV_NAME uv pip install -e "$SCRIPT_DIR/packages/rna_seq"
$CONDA_EXE run -n $ENV_NAME uv pip install -e "$SCRIPT_DIR/packages/docking"
$CONDA_EXE run -n $ENV_NAME uv pip install -e "$SCRIPT_DIR/packages/cli"

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}   Setup Complete Successfully!           ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo -e "\nTo start using bio-analyse, run the following command to activate the environment:"
echo -e "\n    ${YELLOW}conda activate $ENV_NAME${NC}"
echo -e "\nThen try running the help command:"
echo -e "\n    ${YELLOW}bioanalyze --help${NC}"
echo -e "\nHappy analyzing!"
