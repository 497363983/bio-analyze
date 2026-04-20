# Engine Migration Guide

## Summary

The project now provides a shared engine runtime in `bio_analyze_core.engine`.
This is a breaking architectural change intended to replace module-local engine factories and registries with a single reusable model.

The first migrated domains are:

- `quant`
- `docking`

## API Changes

### New Shared API

- `bio_analyze_core.engine.EngineSpec`
- `bio_analyze_core.engine.EngineConfig`
- `bio_analyze_core.engine.EngineContext`
- `bio_analyze_core.engine.BaseEngine`
- `bio_analyze_core.engine.EngineRegistry`
- `bio_analyze_core.engine.EngineManager`
- `bio_analyze_core.engine.register_engine`

### Quant Changes

- `BaseQuantifier` now builds on `BaseEngine`
- New backends should implement `execute()` instead of `_run()`
- `QuantifierRegistry` is now a compatibility facade over the shared `EngineRegistry`
- Quant engines are exposed through `bio_analyze.engine` entry points using names like `quant:salmon`

### Docking Changes

- `BaseDockingEngine` now builds on `BaseEngine`
- `DockingEngineFactory` remains, but internally delegates to the shared engine registry
- Docking engines are exposed through `bio_analyze.engine` entry points using names like `docking:vina`

## Old-To-New Mapping

| Old concept | New concept |
| --- | --- |
| Quantifier-local registry | `EngineRegistry` with domain `quant` |
| Docking factory private `_engines` map | `EngineRegistry` with domain `docking` |
| Module-specific instantiation logic | `EngineManager.create_engine()` |
| `_run()` implementation in new quant backends | `execute()` |

## Migration Steps

### For Quant Backends

1. Update the backend class to inherit from `BaseQuantifier`
2. Replace `_run()` with `execute()`
3. Keep `TOOL_NAME`, `MODE`, and `REQUIRED_BINARIES`
4. Register with `@register_quantifier`
5. Add the backend to the `bio_analyze.engine` entry-point group if it is shipped as a package plugin

### For Docking Engines

1. Keep inheriting from `BaseDockingEngine`
2. Add or confirm `ENGINE_NAME`
3. Accept `**kwargs` in engine constructors so shared context/config injection remains compatible
4. Register through `DockingEngineFactory.register_engine()` or package entry points

### For Other Future Domains

1. Create a domain-specific engine base class on top of `BaseEngine`
2. Define a stable domain name
3. Use `EngineSpec(domain="<domain>", name="<engine>")`
4. Use `EngineManager` for runtime selection and dynamic switching

## Compatibility Notes

- `QuantManager` remains the primary quant orchestration API
- `DockingEngineFactory` remains the primary docking compatibility API
- Existing CLI options for quant and docking do not need to change to adopt the new runtime
- Runtime switching affects future engine instances only; already running tasks are not forcibly migrated

## Rollback Plan

### Code Rollback

1. Revert `bio_analyze_core.engine`
2. Restore the previous quant-local registry implementation
3. Restore the previous docking factory private registry implementation
4. Remove `bio_analyze.engine` entry points from package metadata

### Operational Rollback

- Existing output files such as quant `counts.csv`, manifests, and docking summaries remain data-compatible
- Resume state files are not expected to require structural rollback for current migrated domains
- If plugin discovery causes packaging issues, disable the shared entry points and fall back to in-package registration only

## Common Migration Errors

- Engine constructor rejects `context` or `config`
  - Fix by accepting `**kwargs` and forwarding them to the base class
- Entry point name does not follow `<domain>:<engine_name>`
  - Rename the entry point to the required format
- New quant backend still implements `_run()`
  - Rename the execution method to `execute()`
