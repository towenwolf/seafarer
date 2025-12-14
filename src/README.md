# Seafarer Source Code

This directory contains the source code for the Seafarer data pipeline service.

## Structure

```
src/seafarer/
├── __init__.py          # Package initialization
├── config.py            # Configuration models using Pydantic
├── core/                # Core service logic
│   ├── __init__.py
│   └── pipeline.py      # Pipeline orchestration
├── cli/                 # Command-line interface
│   ├── __init__.py
│   └── main.py          # CLI entry point
└── ports/               # Ports and Adapters (Hexagonal Architecture)
    ├── __init__.py
    ├── base.py          # Abstract base classes for ports
    ├── blob_csv_reader.py    # CSV reader from blob storage
    └── blob_parquet_writer.py # Parquet writer to blob storage
```

## Architecture

Seafarer follows the **Ports and Adapters (Hexagonal Architecture)** pattern:

- **Core**: Contains business logic independent of external systems
- **Ports**: Define interfaces for interacting with external systems
  - `SourcePort`: Abstract interface for reading data
  - `SinkPort`: Abstract interface for writing data
- **Adapters**: Concrete implementations of ports
  - `BlobCsvReader`: Reads CSV from Azure Blob Storage
  - `BlobParquetWriter`: Writes Parquet to Azure Blob Storage

## Usage

### As a Library

```python
from seafarer.core.pipeline import Pipeline
from seafarer.ports.blob_csv_reader import BlobCsvReader
from seafarer.ports.blob_parquet_writer import BlobParquetWriter

# Configure source and sink
source = BlobCsvReader(
    connection_string="...",
    container_name="input-data",
    blob_name="data.csv"
)
sink = BlobParquetWriter(
    connection_string="...",
    container_name="output-data",
    blob_name="data.parquet"
)

# Run pipeline
pipeline = Pipeline(source=source, sink=sink)
pipeline.run()
```

### Via CLI

```bash
seafarer run \
  --source-connection="..." \
  --source-container="input-data" \
  --source-blob="data.csv" \
  --sink-connection="..." \
  --sink-container="output-data" \
  --sink-blob="data.parquet"
```

## Configuration

Configuration is managed using Pydantic models with immutable settings:

```python
from seafarer.config import PipelineConfig, SourceConfig, SinkConfig, BlobStorageConfig

config = PipelineConfig(
    source=SourceConfig(
        blob_storage=BlobStorageConfig(
            connection_string="...",
            container_name="input-data"
        )
    ),
    sink=SinkConfig(
        blob_storage=BlobStorageConfig(
            connection_string="...",
            container_name="output-data"
        )
    ),
    batch_size=1000
)
```

## Development

See the main [README.md](../README.md) for development setup and testing instructions.
