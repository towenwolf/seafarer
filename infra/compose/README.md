# Dual Blob Emulator Infrastructure

This directory contains Docker Compose configurations for running dual Azure Blob Storage emulators using Azurite.

## Overview

The infrastructure consists of two independent blob storage emulators:

1. **blob-source**: Hosts CSV input files for the data pipeline
2. **blob-sink**: Receives Parquet output files from the data pipeline

Both emulators run independently on separate ports and use separate Docker volumes to ensure complete isolation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Seafarer Data Pipeline                    │
│                                                               │
│  ┌──────────────┐                        ┌──────────────┐  │
│  │ Blob Source  │  CSV Input             │  Blob Sink   │  │
│  │  Emulator    │ ──────────► Process ──►│   Emulator   │  │
│  │ Port: 10000  │             Data       │ Port: 10100  │  │
│  └──────────────┘                        └──────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Start Both Emulators

```bash
# Start source emulator
cd blob-source
docker-compose up -d

# Start sink emulator
cd ../blob-sink
docker-compose up -d
```

### Seed Source with CSV Data

```bash
cd blob-source
./seed.sh
```

This will:
- Create the `input-data` container
- Generate a sample CSV file
- Upload the CSV to the source emulator

### Validate Sink for Parquet Output

After running your data pipeline:

```bash
cd blob-sink
./validate.sh
```

This will:
- Check for the output container
- Verify Parquet files exist
- Display file information

### Stop Both Emulators

```bash
# Stop source emulator
cd blob-source
docker-compose down

# Stop sink emulator
cd ../blob-sink
docker-compose down
```

## Emulator Details

### Blob Source Emulator

- **Directory**: `blob-source/`
- **Ports**: 10000 (blob), 10001 (queue), 10002 (table)
- **Container**: `azurite-source`
- **Volume**: `azurite-source-data`
- **Default Input Container**: `input-data`
- **Data Format**: CSV files

See [blob-source/README.md](blob-source/README.md) for detailed documentation.

### Blob Sink Emulator

- **Directory**: `blob-sink/`
- **Ports**: 10100 (blob), 10101 (queue), 10102 (table)
- **Container**: `azurite-sink`
- **Volume**: `azurite-sink-data`
- **Default Output Container**: `output-data`
- **Data Format**: Parquet files

See [blob-sink/README.md](blob-sink/README.md) for detailed documentation.

## Connection Strings

### Source Emulator

```
DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
```

### Sink Emulator

```
DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10100/devstoreaccount1;
```

## Requirements

- Docker and Docker Compose
- Azure CLI (for seed and validation scripts)
- Python with Azure SDK (optional, for programmatic access)

## Common Operations

### Check Emulator Status

```bash
docker ps | grep azurite
```

### View Emulator Logs

```bash
# Source emulator
docker logs azurite-source

# Sink emulator
docker logs azurite-sink
```

### Clean Up All Data

```bash
cd blob-source && docker-compose down -v
cd ../blob-sink && docker-compose down -v
```

## Troubleshooting

### Port Conflicts

If you encounter port conflicts:
1. Check if other services are using ports 10000-10002 or 10100-10102
2. Modify the port mappings in the respective `docker-compose.yml` files
3. Update the connection strings accordingly

### Connection Issues

1. Verify emulators are running: `docker ps | grep azurite`
2. Check emulator logs: `docker logs azurite-source` or `docker logs azurite-sink`
3. Ensure firewall allows connections to the specified ports

### Azure CLI Authentication

The emulators use the well-known Azurite development account key. No additional authentication configuration is needed.

## Integration with Data Pipeline

Your data pipeline should:

1. **Read from Source**: Connect to the source emulator at `http://127.0.0.1:10000/devstoreaccount1`
2. **Process Data**: Convert CSV to Parquet format
3. **Write to Sink**: Connect to the sink emulator at `http://127.0.0.1:10100/devstoreaccount1`

Example Python code:

```python
from azure.storage.blob import BlobServiceClient

# Source connection
source_conn_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
source_client = BlobServiceClient.from_connection_string(source_conn_str)

# Sink connection
sink_conn_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10100/devstoreaccount1;"
sink_client = BlobServiceClient.from_connection_string(sink_conn_str)
```
