# Blob Sink Emulator

This directory contains the configuration for the sink blob storage emulator using Azurite.

## Purpose

The blob-sink emulator receives Parquet output files from the data pipeline after processing.

## Configuration

- **Container Name**: `azurite-sink`
- **Blob Service Port**: `10100` (external) → `10000` (internal)
- **Queue Service Port**: `10101` (external) → `10001` (internal)
- **Table Service Port**: `10102` (external) → `10002` (internal)
- **Storage Account**: `devstoreaccount1`
- **Connection String**: `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10100/devstoreaccount1;`

## Usage

### Start the Emulator

```bash
docker-compose up -d
```

### Validate Parquet Output

The `validate.sh` script will:
1. Wait for the emulator to be ready
2. Check if the output container exists
3. Search for Parquet files in the container
4. Display information about found Parquet files

```bash
./validate.sh
```

To check a different container:

```bash
CONTAINER_NAME=my-output-container ./validate.sh
```

### Manual Verification

List all containers:

```bash
az storage container list \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1' \
  --output table
```

List blobs in a container:

```bash
az storage blob list \
  --container-name 'output-data' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1' \
  --output table
```

Download a Parquet file:

```bash
az storage blob download \
  --container-name 'output-data' \
  --name 'output.parquet' \
  --file 'output.parquet' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1'
```

### Stop the Emulator

```bash
docker-compose down
```

### Clean Up Data

To remove the emulator and all its data:

```bash
docker-compose down -v
```

## Requirements

- Docker and Docker Compose
- Azure CLI (for validation script)

## Port Configuration

The sink emulator uses different external ports (10100-10102) to avoid conflicts with the source emulator (10000-10002). Both emulators can run simultaneously on the same host.

## Expected Output Format

The validation script expects Parquet files with the `.parquet` extension. The pipeline should write processed data to this emulator's blob storage.
