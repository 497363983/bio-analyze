# 开发环境设置

如果您希望参与项目开发或修改代码，请按照以下步骤设置开发环境。

## 使用安装脚本 (install.sh / install.bat)

如果您已经有环境或只想安装 Python 依赖（包括开发工具），可以使用安装脚本：

**Linux / macOS / WSL:**

```bash
bash install.sh
```

**Windows (PowerShell / CMD):**

```cmd
install.bat
```

此脚本会：

1. 检测并安装 `uv`（如果未安装）。
2. 创建 `.venv` 虚拟环境（如果不存在）。
3. 安装所有模块及 `pre-commit`, `commitizen`。
4. 自动配置 Git hooks。

## 手动设置

如果您更喜欢手动设置：

```bash
# 创建虚拟环境
uv venv

# 以可编辑模式安装依赖
uv pip install -e packages/core -e packages/cli -e packages/docking -e packages/plot -e packages/rna_seq

# 安装开发工具
uv pip install pre-commit commitizen

# 安装 git hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

## 代码质量

- **自动检查**：每次 `git commit` 时会自动运行代码格式化和检查。
- **手动检查**：运行 `pre-commit run --all-files` 检查所有文件。
- **规范提交**：建议使用 `cz commit` 来生成符合 Conventional Commits 规范的提交信息。
