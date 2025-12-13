# Seafarer

A data pipeline service with configurable ports (connectors) for blob storage operations.

## Overview

Seafarer provides a clean abstraction for reading and writing data to Azure Blob Storage and compatible emulators. The core service implements ports that are configurable via endpoint and credentials only, without any emulator-specific logic.

## Features

- **Source Port**: `BlobCSVReader` - Reads CSV files from blob storage
- **Sink Port**: `BlobParquetWriter` - Writes Parquet files to blob storage
- **Clean Configuration**: Ports configured via endpoint and credentials only
- **Emulator Agnostic**: Works with Azure Blob Storage and Azurite without special handling
- **Type Safe**: Built with Pydantic for configuration validation

## Installation

Using Poetry:

```bash
poetry install
```

Using pip:

```bash
pip install -e .
```

## Quick Start

### Reading CSV from Blob Storage

```python
from seafarer.config import BlobStorageConfig, SourcePortConfig
from seafarer.ports import BlobCSVReader

# Configure blob storage connection
blob_config = BlobStorageConfig(
    account_name="devstoreaccount1",
    account_key="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
    endpoint="http://127.0.0.1:10000/devstoreaccount1",
    container_name="source-container"
)

# Configure source port
source_config = SourcePortConfig(
    blob_storage=blob_config,
    blob_path="data/input.csv"
)

# Read data
reader = BlobCSVReader(source_config)
try:
    data = reader.read()  # Returns pandas DataFrame
    print(f"Read {len(data)} rows")
finally:
    reader.close()
```

### Writing Parquet to Blob Storage

```python
from seafarer.config import BlobStorageConfig, SinkPortConfig
from seafarer.ports import BlobParquetWriter
import pandas as pd

# Configure blob storage connection
blob_config = BlobStorageConfig(
    account_name="devstoreaccount1",
    account_key="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
    endpoint="http://127.0.0.1:10100/devstoreaccount1",
    container_name="sink-container"
)

# Configure sink port
sink_config = SinkPortConfig(
    blob_storage=blob_config,
    blob_path="data/output.parquet"
)

# Write data
writer = BlobParquetWriter(sink_config)
try:
    data = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
    writer.write(data)
    print("Successfully wrote Parquet file")
finally:
    writer.close()
```

## Architecture

### Ports

Seafarer uses the **Ports and Adapters** (Hexagonal Architecture) pattern:

- **Source Ports**: Read data from external systems (e.g., `BlobCSVReader`)
- **Sink Ports**: Write data to external systems (e.g., `BlobParquetWriter`)

All ports implement abstract base classes (`SourcePort` and `SinkPort`) ensuring consistent interfaces.

### Configuration

Configuration is handled through Pydantic models:

- `BlobStorageConfig`: Blob storage connection details (account, key, endpoint, container)
- `SourcePortConfig`: Source port configuration (blob storage + blob path)
- `SinkPortConfig`: Sink port configuration (blob storage + blob path)

All configuration models are immutable (frozen) to prevent accidental modifications.

## Development

### Running Tests

```bash
poetry run pytest
```

With coverage:

```bash
poetry run pytest --cov=seafarer --cov-report=html
```

### Code Quality

Format code:

```bash
poetry run black src/ tests/
```

Lint code:

```bash
poetry run ruff check src/ tests/
```

Type check:

```bash
poetry run mypy src/
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py`: CSV to Parquet conversion pipeline

## License

MIT License - see LICENSE file for details.