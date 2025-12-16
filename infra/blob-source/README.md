# Blob Source Emulator

This directory contains the configuration for the source blob storage emulator using Azurite.

## Purpose

The blob-source emulator hosts CSV input files that will be processed by the data pipeline.

## Configuration

- **Container Name**: `azurite-source`
- **Blob Service Port**: `10000`
- **Queue Service Port**: `10001`
- **Table Service Port**: `10002`
- **Storage Account**: `devstoreaccount1`
- **Connection String**: `DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;`

## Usage

### Start the Emulator

```bash
docker compose up -d
```

### Seed with CSV Data

The `seed.sh` script will:
1. Wait for the emulator to be ready
2. Create the `input-data` container
3. Generate a sample CSV file (if not provided)
4. Upload the CSV file to the container

```bash
./seed.sh
```

To upload a custom CSV file:

```bash
CSV_FILE=/path/to/your/data.csv ./seed.sh
```

### Verify Data

List the blobs in the container:

```bash
az storage blob list \
  --container-name 'input-data' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10000/devstoreaccount1' \
  --output table
```

### Stop the Emulator

```bash
docker compose down
```

### Clean Up Data

To remove the emulator and all its data:

```bash
docker compose down -v
```

## Requirements

- Docker and Docker Compose
- Azure CLI (for seeding script)

## Default CSV Schema

The sample CSV file contains the following columns:
- `id`: Integer identifier
- `name`: Person's full name
- `email`: Email address
- `age`: Age in years
- `city`: City of residence
- `signup_date`: Date of signup (YYYY-MM-DD format)
