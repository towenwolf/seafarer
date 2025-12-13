"""Example usage of seafarer ports for CSV to Parquet conversion.

This example demonstrates how to:
1. Configure source and sink ports with endpoint and credentials
2. Read CSV data from blob storage
3. Write data as Parquet to blob storage

Note: This example works with both Azure Blob Storage and Azurite emulator.
No emulator-specific logic is present in the port implementations.
"""

from seafarer.config import BlobStorageConfig, SourcePortConfig, SinkPortConfig
from seafarer.ports import BlobCSVReader, BlobParquetWriter


def main() -> None:
    """Run the CSV to Parquet pipeline."""
    
    # Configure source blob storage (for reading CSV)
    source_blob_config = BlobStorageConfig(
        account_name="devstoreaccount1",
        account_key="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        endpoint="http://127.0.0.1:10000/devstoreaccount1",
        container_name="source-container"
    )
    
    # Configure sink blob storage (for writing Parquet)
    sink_blob_config = BlobStorageConfig(
        account_name="devstoreaccount1",
        account_key="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
        endpoint="http://127.0.0.1:10100/devstoreaccount1",
        container_name="sink-container"
    )
    
    # Configure source port
    source_config = SourcePortConfig(
        blob_storage=source_blob_config,
        blob_path="data/input.csv"
    )
    
    # Configure sink port
    sink_config = SinkPortConfig(
        blob_storage=sink_blob_config,
        blob_path="data/output.parquet"
    )
    
    # Create ports
    reader = BlobCSVReader(source_config)
    writer = BlobParquetWriter(sink_config)
    
    try:
        # Read CSV data
        print("Reading CSV data from blob storage...")
        data = reader.read()
        print(f"Read {len(data)} rows")
        print(f"Columns: {', '.join(data.columns)}")
        
        # Write as Parquet
        print("\nWriting Parquet data to blob storage...")
        writer.write(data)
        print("Successfully wrote Parquet file")
        
    finally:
        # Clean up resources
        reader.close()
        writer.close()
        print("\nClosed all connections")


if __name__ == "__main__":
    main()
