# seafarer

A data pipeline infrastructure with dual blob storage emulators for CSV-to-Parquet processing.

## Overview

Seafarer provides a complete infrastructure setup for data processing pipelines using Azure Blob Storage emulators (Azurite). The system consists of:

- **Source Emulator**: Hosts CSV input files
- **Sink Emulator**: Receives Parquet output files
- **Seed Scripts**: Automate CSV data upload
- **Validation Scripts**: Verify Parquet output

## Quick Start

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

### Validate Output

```bash
cd infra/compose/blob-sink
./validate.sh
```

## Documentation

- [Infrastructure Overview](infra/compose/README.md)
- [Blob Source Configuration](infra/compose/blob-source/README.md)
- [Blob Sink Configuration](infra/compose/blob-sink/README.md)
- [Testing Guide](infra/compose/TESTING.md)

## Architecture

```
CSV Input → Source Emulator (10000) → Pipeline → Sink Emulator (10100) → Parquet Output
```

## Requirements

- Docker and Docker Compose
- Azure CLI (for scripts)

## License

See [LICENSE](LICENSE) file for details.