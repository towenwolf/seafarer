# seafarer

A data pipeline infrastructure with dual blob storage emulators for CSV-to-Parquet processing.

## Overview

Seafarer provides a complete infrastructure setup for data processing pipelines using Azure Blob Storage emulators (Azurite). The system consists of:

- **Source Emulator**: Hosts CSV input files
- **Sink Emulator**: Receives Parquet output files
- **Seed Scripts**: Automate CSV data upload
- **Validation Scripts**: Verify Parquet output

## Quick Start

### Installation

Install the Seafarer package and its dependencies:

```bash
pip install -e .
```

For development with testing tools:

```bash
pip install -e ".[dev]"
```

### Start the Infrastructure

```bash
# Start source emulator
cd infra/compose/blob-source
docker compose up -d

# Start sink emulator
cd ../blob-sink
docker compose up -d
```

### Seed with Sample Data

```bash
cd infra/compose/blob-source
./seed.sh
```

### Run the Pipeline

Using the CLI:

```bash
seafarer run \
  --source-connection="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;" \
  --source-container="input-data" \
  --source-blob="data.csv" \
  --sink-connection="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10100/devstoreaccount1;" \
  --sink-container="output-data" \
  --sink-blob="data.parquet"
```

Or programmatically:

```python
from seafarer.core.pipeline import Pipeline
from seafarer.ports.blob_csv_reader import BlobCsvReader
from seafarer.ports.blob_parquet_writer import BlobParquetWriter

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

pipeline = Pipeline(source=source, sink=sink)
pipeline.run()
```

### Validate Output

```bash
cd infra/compose/blob-sink
./validate.sh
```

## Project Structure

```
seafarer/
├── src/seafarer/          # Main package source code
│   ├── core/              # Core business logic
│   ├── cli/               # Command-line interface
│   ├── ports/             # Ports & Adapters (Hexagonal Architecture)
│   └── config.py          # Configuration models
├── tests/                 # Test suite
├── infra/compose/         # Docker infrastructure
│   ├── blob-source/       # Source emulator setup
│   └── blob-sink/         # Sink emulator setup
└── pyproject.toml         # Package configuration
```

See [src/README.md](src/README.md) for detailed code documentation.

## Documentation

- [Source Code Documentation](src/README.md)
- [Infrastructure Overview](infra/compose/README.md)
- [Blob Source Configuration](infra/compose/blob-source/README.md)
- [Blob Sink Configuration](infra/compose/blob-sink/README.md)
- [Testing Guide](infra/compose/TESTING.md)

## Architecture

Seafarer follows the **Ports and Adapters (Hexagonal Architecture)** pattern:

```
CSV Input → Source Emulator (10000) → Pipeline → Sink Emulator (10100) → Parquet Output
                                          ↓
                                      Core Logic
                                          ↓
                                    SourcePort ← BlobCsvReader
                                    SinkPort   ← BlobParquetWriter
```

- **Core**: Business logic independent of external systems
- **Ports**: Interfaces for external system interactions (SourcePort, SinkPort)
- **Adapters**: Concrete implementations (BlobCsvReader, BlobParquetWriter)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

## Requirements

- Python >= 3.8
- Docker and Docker Compose
- Azure CLI (for infrastructure scripts)

## License

See [LICENSE](LICENSE) file for details.