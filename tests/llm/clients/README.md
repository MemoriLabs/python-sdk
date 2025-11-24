# LLM Client Tests

This directory contains integration tests for various LLM clients in the `oss/` directory.

## Directory Structure

- `oss/` - Tests for LLM client integrations

## Test Modes

The same test files can be run in two different modes using the `MEMORI_ENTERPRISE` environment variable:

### OSS Mode (Default)
When `MEMORI_ENTERPRISE` is not set or set to `0`:
- All memory data is written to your local database
- No API calls are made to Memori's servers
- Requires a database connection (PostgreSQL, MySQL, MongoDB, or SQLite)

Example:
```bash
# Locally with uv
OPENAI_API_KEY=sk-... uv run python tests/llm/clients/oss/openai/sync.py

# Or with Docker/Make
make run-integration FILE=tests/llm/clients/oss/openai/sync.py
```

### Enterprise Mode
When `MEMORI_ENTERPRISE=1` is set:
- Memory data would be sent to Memori's API endpoint for processing
- Requires `MEMORI_API_KEY` to be set

**Note:** Enterprise mode is not fully implemented yet. When enabled, you'll see a warning:
```
RuntimeWarning: Enterprise mode is not fully implemented yet. Falling back to local Writer mode.
```

The tests will still run and write to the local database as a fallback.

Example:
```bash
# Locally with uv
MEMORI_ENTERPRISE=1 MEMORI_API_KEY=your-key OPENAI_API_KEY=sk-... uv run python tests/llm/clients/oss/openai/sync.py

# Or with Docker/Make
make run-integration-enterprise FILE=tests/llm/clients/oss/openai/sync.py
```

## Environment Variables

- `MEMORI_ENTERPRISE` - Set to `"1"` to enable enterprise mode
- `MEMORI_API_KEY` - API key for Memori's enterprise service
- `MEMORI_TEST_MODE` - Set to `"1"` to enable test mode (prevents actual API calls in Collector)
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / etc. - LLM provider API keys

## When Enterprise Mode is Ready

Once enterprise mode is fully implemented:
1. Setting `MEMORI_ENTERPRISE=1` will call `Collector(config).fire_and_forget(payload)` instead of `Writer`
2. Conversation data will be sent to Memori's API for processing
3. Data will not be written to the local database (unless configured otherwise)

See `memori/memory/_manager.py` for the TODO comment marking where enterprise mode needs to be completed.
