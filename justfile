set shell := ["powershell.exe", "-c"]

default:
    @just --list

# Format code with Black
[group('linters')]
format:
    uv run black .

# Check code formatting with Black and ruff
[group('linters')]
check:
    uv run ruff check .
    uv run black . --check

# Fix code formatting with ruff
[group('linters')]
uv-fix:
    uv run ruff check . --fix

# Run all tests (without coverage)
[group('testing')]
test-all:
    uv run pytest

# Run all tests with coverage
[group('testing')]
test-all-coverage:
    uv run pytest --cov=src --cov-report=term-missing

# Run e2e tests for grpc server
[group('testing')]
test-grpc:
    uv run pytest tests/test_schedule_servicer.py -s -v

# Run e2e tests for API
[group('testing')]
test-api:
    uv run pytest tests/test_schedule_api.py -s -v

# Run unit tests for next takings feature
[group('testing')]
test-next-takings:
    uv run pytest tests/test_schedule_utils.py -s -v

# Start the application in docker
[group('docker')]
docker-start:
    docker compose up --build

# Start the application locally
[group('app')]
app-start:
    uv run python -m src.main

# Generate schemas from openapi.yaml (codegeneration)
[group('app')]
generate-schemas:
    uv run datamodel-codegen --input docs/openapi.yaml --input-file-type openapi --output src/api/v1/schedule/schemas/generated_schemas.py --disable-timestamp
