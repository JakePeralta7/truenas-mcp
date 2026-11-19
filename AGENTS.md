# Agent Instructions

This file provides guidance for AI agents working with the truenas-mcp codebase.

## Project Overview

truenas-mcp is an MCP (Model Context Protocol) server that exposes the TrueNAS WebSocket JSON-RPC 2.0 API as MCP tools. It follows the same architectural patterns as forgejo-mcp.

## Architecture

- **server.py**: Main entry point, settings, MCP server instance, global client management
- **client.py**: TrueNAS client wrapper (sync-compatible async), filter/option builders
- **helpers/**: Domain modules, each registering tools via `@mcp.tool` decorator

## Key Patterns

### Settings & Configuration
- All config from environment variables (see README.md)
- `load_settings()` in server.py validates and returns Settings dataclass
- Global `READ_ONLY_MODE` controls write tool registration

### Client Wrapper
- `TruenasClientWrapper` wraps `pytruenas.TrueNASClient`
- Provides sync-compatible interface via `_run_async()`
- Single persistent WebSocket connection (created at startup)

### Tool Registration
- Read tools: `@mcp.tool(annotations=READ_ONLY)`
- Write tools: Conditionally registered via `_register_*()` functions that check `READ_ONLY_MODE`
- Each tool has a `do_*` internal function (for testing) and a public `@mcp.tool` function

### Error Handling
- `@truenas_errors` decorator converts exceptions to `RuntimeError` (MCP isError)
- Correlation IDs for request tracing via contextvar
- Structured logging to stderr

### Query Helpers
- `build_filters(**kwargs)` - Convert kwargs to TrueNAS filter format `[[field, "=", value]]`
- `build_options(limit, offset, order_by, select, count)` - Build query options dict
- `build_filter_or()` / `build_filter_and()` - Complex filters

## Adding New Tools

1. Create or edit appropriate helper in `helpers/`
2. Add `do_*` internal function with `@truenas_errors` decorator
3. Add public tool function with `@mcp.tool` decorator
4. For write tools, wrap in `_register_*` function that checks `READ_ONLY_MODE`
5. Import helper in `server.py` for side-effect registration

## Testing

```bash
pytest                    # Run all tests
pytest tests/test_pool.py # Run specific test file
pytest -k "list_pools"    # Run specific test
```

## Type Checking

```bash
pyright
```

## Code Style

- Python 3.12+ (match args, pattern matching available)
- Type hints required for all public functions
- Docstrings for all tools (become MCP tool descriptions)
- Async functions for all API calls
- Redact sensitive data in logs (`_safe_args` in server.py)