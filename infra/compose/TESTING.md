# Testing Dual Blob Emulators

This document provides step-by-step instructions for testing the dual blob emulator infrastructure.

## Prerequisites

- Docker and Docker Compose installed
- Azure CLI installed (`az`)
- bash shell

## Complete Test Workflow

### 1. Start Both Emulators

```bash
# Start the source emulator
cd blob-source
docker compose up -d

# Start the sink emulator
cd ../blob-sink
docker compose up -d

# Verify both are running
docker ps | grep azurite
```

Expected output:
```
azurite-sink     Up X seconds    0.0.0.0:10100->10000/tcp, ...
azurite-source   Up X seconds    0.0.0.0:10000->10000/tcp, ...
```

### 2. Seed the Source Emulator with CSV Data

```bash
cd blob-source
./seed.sh
```

Expected output:
```
=== Seeding Blob Source Emulator ===
Endpoint: http://127.0.0.1:10000/devstoreaccount1
Container: input-data
CSV File: sample.csv

Waiting for blob source emulator to be ready...
Emulator is ready!
Creating container 'input-data'...
Creating sample CSV file...
Sample CSV file created: sample.csv
Uploading CSV file to blob storage...

✓ Successfully seeded blob source emulator!
✓ Container: input-data
✓ File: sample.csv
```

### 3. Verify Source Data

List the CSV files in the source emulator:

```bash
az storage blob list \
  --container-name 'input-data' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10000/devstoreaccount1' \
  --output table
```

Expected output:
```
Name        Blob Type    Blob Tier    Length    Content Type    Last Modified
----------  -----------  -----------  --------  --------------  -------------------------
sample.csv  BlockBlob    Hot          655       text/csv        2025-XX-XXX...
```

### 4. Simulate Data Pipeline (Manual Test)

In a real scenario, your data pipeline would:
1. Read CSV from source emulator (port 10000)
2. Process and convert to Parquet
3. Write to sink emulator (port 10100)

For testing purposes, create a mock Parquet file:

```bash
# Create a mock parquet file
cd blob-sink
echo "PAR1 mock parquet data" > test_output.parquet

# Create output container
az storage container create \
  --name 'output-data' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1'

# Upload parquet file
az storage blob upload \
  --container-name 'output-data' \
  --name 'test_output.parquet' \
  --file 'test_output.parquet' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1' \
  --overwrite
```

### 5. Validate Sink Emulator

Run the validation script to confirm Parquet files exist:

```bash
cd blob-sink
./validate.sh
```

Expected output:
```
=== Validating Blob Sink Emulator ===
Endpoint: http://127.0.0.1:10100/devstoreaccount1
Container: output-data
Looking for: *.parquet

Waiting for blob sink emulator to be ready...
Emulator is ready!
Checking if container 'output-data' exists...
✓ Container 'output-data' exists

Listing blobs in container 'output-data'...
✓ Found 1 Parquet file(s) in container 'output-data'

Parquet files:
  - test_output.parquet
    Size: X KB (X bytes)

✓ Validation successful!
✓ Parquet files exist in blob sink emulator
```

### 6. Clean Up

Stop and remove emulators (keeping data):

```bash
cd blob-source
docker compose down

cd ../blob-sink
docker compose down
```

Stop and remove emulators with all data:

```bash
cd blob-source
docker compose down -v

cd ../blob-sink
docker compose down -v
```

## Automated Test Script

You can create an automated test script:

```bash
#!/bin/bash
set -e

echo "=== Testing Dual Blob Emulators ==="

# Start emulators
echo "Starting emulators..."
cd blob-source && docker compose up -d
cd ../blob-sink && docker compose up -d
sleep 5

# Seed source
echo "Seeding source emulator..."
cd ../blob-source
./seed.sh

# Simulate pipeline (upload test parquet)
echo "Simulating data pipeline..."
cd ../blob-sink
echo "PAR1 mock" > test.parquet
az storage container create \
  --name 'output-data' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1'
az storage blob upload \
  --container-name 'output-data' \
  --name 'test.parquet' \
  --file 'test.parquet' \
  --account-name 'devstoreaccount1' \
  --account-key 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==' \
  --blob-endpoint 'http://127.0.0.1:10100/devstoreaccount1' \
  --overwrite

# Validate sink
echo "Validating sink emulator..."
./validate.sh

echo "=== All tests passed! ==="
```

## Common Issues

### Issue: Port already in use

**Solution**: Check if another service is using ports 10000-10002 or 10100-10102:
```bash
lsof -i :10000
lsof -i :10100
```

### Issue: Azure CLI hangs

**Solution**: Ensure the emulator has fully started. Wait 5-10 seconds after `docker compose up -d` before running Azure CLI commands.

### Issue: Connection refused

**Solution**: Verify emulators are running:
```bash
docker ps | grep azurite
docker logs azurite-source
docker logs azurite-sink
```

## Performance Notes

- Source emulator: Optimized for read operations (CSV input)
- Sink emulator: Optimized for write operations (Parquet output)
- Both emulators can handle concurrent operations
- Data persists in Docker volumes between restarts (unless using `docker compose down -v`)

## Security Notes

These emulators use the well-known Azurite development account credentials:
- Account Name: `devstoreaccount1`
- Account Key: `Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==`

**WARNING**: These credentials are for development/testing only. Never use in production!
