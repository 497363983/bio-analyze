# Core Module Configuration

The `bio-analyze-core` module provides the foundational infrastructure for the entire toolkit. While primarily used internally by other modules, it offers some global configuration options for users.

## Logging Configuration

You can control the verbosity of the tool using environment variables or configuration files.

### Log Levels

Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

Default level is `INFO`.

### Configuration

You can typically set the log level via the CLI of specific tools, or by setting the `BIO_ANALYZE_LOG_LEVEL` environment variable (if supported by the specific tool wrapper).

## Global Configuration

The toolkit supports loading configuration from `config.json` or `config.yaml` files. Most modules accept a `--config` parameter.

Example `config.yaml`:

```yaml
# Global settings
output_dir: ./results
threads: 4

# Module specific settings
docking:
  exhaustiveness: 8

plot:
  theme: nature
```
