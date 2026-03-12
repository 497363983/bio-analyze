.PHONY: lint format check

lint:
	uv run ruff check packages scripts

format:
	uv run ruff format packages scripts

check:
	uv run ruff check packages scripts
	uv run ruff format --check packages scripts
