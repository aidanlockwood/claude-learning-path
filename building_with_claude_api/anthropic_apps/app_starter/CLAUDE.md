# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python package implementing document-related tools (conversion, processing), exposed through an MCP (Model Context Protocol) server so AI assistants can call them.

## Setup & commands

```bash
# Create and activate a virtual env
uv venv
source .venv/bin/activate

# Install the package in editable mode (run after adding/changing dependencies in pyproject.toml)
uv pip install -e .

# Start the MCP server
uv run main.py

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_docx
```

Note: `source .venv/bin/activate` only persists within a single shell session. When running commands one-off (e.g. via separate tool calls), prefer `uv run ...` over assuming the venv is active.

## Architecture

- `main.py` — creates the `FastMCP` server instance (`mcp = FastMCP("docs")`) and is the single place where tool functions are registered with `mcp.tool()(fn)`. A function existing in `tools/` does **not** make it available to the server — it must be explicitly registered here.
- `tools/` — plain Python functions implementing tool logic, decoupled from MCP. Each module groups related tools (e.g. `tools/document.py` for document conversion, `tools/math.py` for arithmetic). Functions are written to be MCP-tool-ready (see "Defining MCP tools" below) but are just regular functions otherwise — testable without spinning up the server.
- `tests/` — pytest tests against the `tools/` functions directly (not through the MCP server). Binary fixtures for document-conversion tests live in `tests/fixtures/`.

When adding a new tool: implement it in the appropriate `tools/*.py` module (or a new module), then register it in `main.py` with `mcp.tool()(my_function)`.

## Defining MCP tools

Tools are plain Python functions registered with the MCP server via `mcp.tool()(my_function)` in `main.py`.

Tool docstrings double as the tool description surfaced to the model, so they must be self-contained and should:

- Begin with a one-line summary
- Provide a detailed explanation of functionality
- Explain when to use (and not use) the tool
- Include usage examples with expected input/output

Parameters should use `Field` from `pydantic` to describe each argument's purpose to the model, e.g.:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does")
) -> ReturnType:
    """One-line summary.

    Detailed explanation of functionality.

    When to use:
    - ...

    Examples:
    >>> my_tool("x", 1)
    ...
    """
    # Implementation
```

See `tools/math.py`'s `add` for a minimal example of this pattern already registered in `main.py`, and `tools/document.py`'s `binary_document_to_markdown` for a tool implementation that is not yet registered.
