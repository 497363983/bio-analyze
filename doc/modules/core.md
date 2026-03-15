# bio-analyze-core

The `bio-analyze-core` module provides the infrastructure for the entire toolkit. Although primarily used internally by other modules, it also provides some user-configurable global options.

## Log Configuration

You can control the log detail level of the tool via environment variables or configuration files.

### Log Levels

Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

Default level is `INFO`.

### Configuration Methods

Usually can be set via specific tool CLI parameters, or by setting the `BIO_ANALYZE_LOG_LEVEL` environment variable (if supported by the specific tool wrapper).

## Global Configuration

The toolkit supports loading configuration from `config.json` or `config.yaml` files. Most modules accept the `--config` parameter.

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
