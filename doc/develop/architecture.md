# Architecture

## Monorepo Structure

- `packages/core`: Common capabilities (configuration, logging, IO, external command execution, resource management, etc.).
- `packages/cli`: Unified command-line entry point, supporting plugin-based loading of module subcommands.
- `packages/*`: Analysis tool modules (e.g., rna-seq, docking), each being an independently publishable package.

## Design Principles

- **Independent Release, On-Demand Installation**: Each tool module is an independent distribution package, registering CLI subcommands via entry points.
- **Common Logic Abstraction**: Cross-module reusable functions are centralized in `core`.
- **Parallel CLI & Python API**: The same capability can be called via command line or imported as a library.
