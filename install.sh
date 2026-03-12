#!/bin/bash

# bio-analyse install script (Linux/macOS)
# Installs all dependencies including pre-commit and commitizen, and configures git hooks.

set -e

# Define colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   Bio-Analyze Install Script             ${NC}"
echo -e "${GREEN}==========================================${NC}"


# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    uv venv
fi

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
# Install all packages in editable mode
uv pip install -e packages/core
uv pip install -e packages/plot
uv pip install -e packages/rna_seq
uv pip install -e packages/docking
uv pip install -e packages/cli

# Install dev dependencies
echo -e "\n${YELLOW}Installing dev dependencies (pre-commit, commitizen)...${NC}"
uv pip install pre-commit commitizen

# Configure pre-commit hooks
echo -e "\n${YELLOW}Configuring pre-commit hooks...${NC}"
if [ -d ".git" ]; then
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg
    echo -e "${GREEN}Pre-commit hooks installed successfully.${NC}"
else
    echo -e "${YELLOW}Not a git repository. Skipping pre-commit hook installation.${NC}"
fi

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}   Installation Complete!                 ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo -e "\nTo activate the environment, run:"
echo -e "    ${YELLOW}source .venv/bin/activate${NC}"
