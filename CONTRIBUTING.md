# Contributing to Memori Python SDK

Thank you for your interest in contributing to Memori!

## Development Setup

We use Docker for a consistent development environment. Get started with one command:

### Quick Start

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys (optional for unit tests)
# Required for integration tests: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY

# Start the environment
make dev-up
```

This will:
- Build the Docker container with Python 3.12
- Install all dependencies automatically
- Start PostgreSQL for integration tests

### Development Commands

```bash
# Enter the development container
make dev-shell

# Run unit tests (fast, no external dependencies)
make test

# Initialize database schema (first time only)
make init-db

# Run integration tests (requires API keys and database)
make test-integration

# Run a specific integration test script
make run-integration FILE=tests/llm/clients/oss/openai/async.py

# Format code with ruff
make format

# Check linting
make lint

# Stop the environment
make dev-down

# Clean up everything (containers, volumes, cache)
make clean
```

## Testing

### Unit Tests
Unit tests use mocks and run without external dependencies:
```bash
make test
```

### Integration Tests
Integration tests use real PostgreSQL database and LLM APIs:
```bash
# Set API keys in .env first
make init-db
make test-integration
```

## Requirements

- Docker
- Docker Compose
- Make

## Project Structure

```
memori/              # SDK source code
tests/               # Test files
  database/          # Integration test helpers
  llm/               # LLM provider tests
  memory/            # Memory system tests
  storage/           # Storage adapter tests
conftest.py          # Pytest fixtures
```

## Code Quality

- Format code with `make format` (uses ruff)
- Check linting with `make lint`
- All tests must pass before submitting PR

## Notes

- Docker files (Dockerfile, docker-compose.yml, Makefile) are for development only
- They are NOT included in the PyPI package
- The SDK has no backend dependencies - fully self-contained
