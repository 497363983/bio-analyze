# Architecture

## Monorepo Structure

- `packages/core`: Common capabilities (configuration, logging, IO, subprocess management, resource management, etc.).
- `packages/cli`: Unified command-line entry point, supporting plugin-based loading of module subcommands.
- `packages/*`: Analysis tool modules (e.g., rna-seq, docking), each being an independently publishable package.

## Design Principles

- **Modular & Independent**: Each tool is an independent package, registered via entry points.
- **Common Logic Abstracted**: Reusable functions are centralized in `core`.
- **CLI & Python API**: Unified capabilities callable via command line or imported as a library.
