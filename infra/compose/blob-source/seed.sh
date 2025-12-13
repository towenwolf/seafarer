#!/bin/bash
set -e

# Configuration
STORAGE_ACCOUNT="devstoreaccount1"
STORAGE_KEY="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
BLOB_ENDPOINT="http://127.0.0.1:10000/devstoreaccount1"
CONTAINER_NAME="input-data"
CSV_FILE="${CSV_FILE:-sample.csv}"

echo "=== Seeding Blob Source Emulator ==="
echo "Endpoint: $BLOB_ENDPOINT"
echo "Container: $CONTAINER_NAME"
echo "CSV File: $CSV_FILE"
echo ""

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI (az) is not installed"
    echo "Please install Azure CLI: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Wait for emulator to be ready
echo "Waiting for blob source emulator to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if nc -z 127.0.0.1 10000 2>/dev/null || (command -v timeout &> /dev/null && timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/10000" 2>/dev/null); then
        echo "Emulator is ready!"
        sleep 2  # Give it a moment to fully initialize
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - waiting..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Blob source emulator did not become ready in time"
    exit 1
fi

# Create container
echo "Creating container '$CONTAINER_NAME'..."
az storage container create \
    --name "$CONTAINER_NAME" \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --blob-endpoint "$BLOB_ENDPOINT" \
    --only-show-errors || true

# Create a sample CSV file if it doesn't exist
if [ ! -f "$CSV_FILE" ]; then
    echo "Creating sample CSV file..."
    cat > "$CSV_FILE" << 'EOF'
id,name,email,age,city,signup_date
1,John Doe,john.doe@example.com,28,New York,2023-01-15
2,Jane Smith,jane.smith@example.com,34,San Francisco,2023-02-20
3,Bob Johnson,bob.johnson@example.com,45,Chicago,2023-03-10
4,Alice Williams,alice.williams@example.com,29,Boston,2023-04-05
5,Charlie Brown,charlie.brown@example.com,52,Seattle,2023-05-12
6,Diana Prince,diana.prince@example.com,31,Los Angeles,2023-06-18
7,Edward Norton,edward.norton@example.com,38,Austin,2023-07-22
8,Fiona Green,fiona.green@example.com,27,Denver,2023-08-30
9,George Harris,george.harris@example.com,41,Miami,2023-09-14
10,Helen Clark,helen.clark@example.com,36,Portland,2023-10-25
EOF
    echo "Sample CSV file created: $CSV_FILE"
fi

# Upload CSV file to blob storage
echo "Uploading CSV file to blob storage..."
az storage blob upload \
    --container-name "$CONTAINER_NAME" \
    --name "$(basename "$CSV_FILE")" \
    --file "$CSV_FILE" \
    --account-name "$STORAGE_ACCOUNT" \
    --account-key "$STORAGE_KEY" \
    --blob-endpoint "$BLOB_ENDPOINT" \
    --only-show-errors \
    --overwrite

echo ""
echo "✓ Successfully seeded blob source emulator!"
echo "✓ Container: $CONTAINER_NAME"
echo "✓ File: $(basename "$CSV_FILE")"
echo ""
echo "To verify, you can list the blobs:"
echo "az storage blob list \\"
echo "  --container-name '$CONTAINER_NAME' \\"
echo "  --account-name '$STORAGE_ACCOUNT' \\"
echo "  --account-key '$STORAGE_KEY' \\"
echo "  --blob-endpoint '$BLOB_ENDPOINT' \\"
echo "  --output table"
