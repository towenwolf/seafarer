#!/bin/bash
set -e

# Configuration
STORAGE_ACCOUNT="devstoreaccount1"
STORAGE_KEY="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
BLOB_ENDPOINT="http://127.0.0.1:10100/devstoreaccount1"
CONTAINER_NAME="${CONTAINER_NAME:-output-data}"
PARQUET_FILE="${PARQUET_FILE:-*.parquet}"

echo "=== Validating Blob Sink Emulator ==="
echo "Endpoint: $BLOB_ENDPOINT"
echo "Container: $CONTAINER_NAME"
echo "Looking for: $PARQUET_FILE"
echo ""

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI (az) is not installed"
    echo "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Wait for emulator to be ready
echo "Waiting for blob sink emulator to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -o /dev/null -w "%{http_code}" "$BLOB_ENDPOINT" | grep -q "400\|404"; then
        echo "Emulator is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - waiting..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Blob sink emulator did not become ready in time"
    exit 1
fi

# Check if container exists
echo "Checking if container '$CONTAINER_NAME' exists..."
if ! az storage container exists \
    --name "$CONTAINER_NAME" \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --blob-endpoint "$BLOB_ENDPOINT" \
    --only-show-errors | grep -q '"exists": true'; then
    echo "✗ Container '$CONTAINER_NAME' does not exist"
    echo ""
    echo "Available containers:"
    az storage container list \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --blob-endpoint "$BLOB_ENDPOINT" \
        --output table 2>/dev/null || echo "No containers found"
    exit 1
fi

echo "✓ Container '$CONTAINER_NAME' exists"
echo ""

# List all blobs in the container
echo "Listing blobs in container '$CONTAINER_NAME'..."
blobs=$(az storage blob list \
    --container-name "$CONTAINER_NAME" \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --blob-endpoint "$BLOB_ENDPOINT" \
    --only-show-errors \
    --output json 2>/dev/null || echo "[]")

# Check if any parquet files exist
parquet_count=$(echo "$blobs" | grep -c '\.parquet"' || true)

if [ "$parquet_count" -eq 0 ]; then
    echo "✗ No Parquet files found in container '$CONTAINER_NAME'"
    echo ""
    echo "All files in container:"
    echo "$blobs" | grep -o '"name": "[^"]*"' | sed 's/"name": "//;s/"$//' || echo "  (empty)"
    exit 1
fi

echo "✓ Found $parquet_count Parquet file(s) in container '$CONTAINER_NAME'"
echo ""
echo "Parquet files:"
echo "$blobs" | grep '\.parquet"' | grep -o '"name": "[^"]*"' | sed 's/"name": "//;s/"$//' | while read -r file; do
    echo "  - $file"
    
    # Get blob properties
    size=$(echo "$blobs" | grep -A 5 "\"name\": \"$file\"" | grep '"contentLength":' | grep -o '[0-9]*' | head -1)
    if [ -n "$size" ]; then
        size_kb=$((size / 1024))
        echo "    Size: ${size_kb} KB (${size} bytes)"
    fi
done

echo ""
echo "✓ Validation successful!"
echo "✓ Parquet files exist in blob sink emulator"

# Optional: Download and inspect parquet files
if command -v parquet-tools &> /dev/null || command -v parquet &> /dev/null; then
    echo ""
    echo "Parquet tools detected. To inspect files, you can download them:"
    echo "$blobs" | grep '\.parquet"' | grep -o '"name": "[^"]*"' | sed 's/"name": "//;s/"$//' | while read -r file; do
        echo "az storage blob download \\"
        echo "  --container-name '$CONTAINER_NAME' \\"
        echo "  --name '$file' \\"
        echo "  --file '$file' \\"
        echo "  --account-name '$STORAGE_ACCOUNT' \\"
        echo "  --account-key '$STORAGE_KEY' \\"
        echo "  --blob-endpoint '$BLOB_ENDPOINT'"
    done
fi
