# 核心模块配置

`bio-analyze-core` 模块为整个工具箱提供了基础设施。虽然主要供其他模块内部调用，但也提供了一些用户可配置的全局选项。

## 日志配置

您可以通过环境变量或配置文件控制工具的日志详细程度。

### 日志级别

支持的级别：`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`。

默认级别为 `INFO`。

### 配置方式

通常可以通过具体工具的 CLI 参数设置，或者设置 `BIO_ANALYZE_LOG_LEVEL` 环境变量（如果具体工具封装支持）。

## 全局配置

工具箱支持从 `config.json` 或 `config.yaml` 文件加载配置。大多数模块都接受 `--config` 参数。

示例 `config.yaml`:

```yaml
# 全局设置
output_dir: ./results
threads: 4

# 模块特定设置
docking:
  exhaustiveness: 8

plot:
  theme: nature
```
