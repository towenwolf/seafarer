"""Blob Parquet Writer sink port implementation."""

from io import BytesIO
from typing import Optional

import pandas as pd
from azure.storage.blob import BlobServiceClient

from seafarer.config import SinkPortConfig
from seafarer.ports.base import SinkPort


class BlobParquetWriter(SinkPort):
    """Sink port that writes Parquet files to Azure Blob Storage.
    
    This port is configured via endpoint and credentials only, with no
    emulator-specific logic. It works with both Azure Blob Storage and
    compatible blob storage emulators like Azurite.
    """

    def __init__(self, config: SinkPortConfig) -> None:
        """Initialize the BlobParquetWriter.
        
        Args:
            config: Configuration for the sink port including blob storage
                   endpoint, credentials, container, and blob path.
        """
        self._config = config
        self._client: Optional[BlobServiceClient] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Azure Blob Service Client using configuration."""
        blob_config = self._config.blob_storage
        
        # Construct connection string from configuration
        # This works with both Azure Blob Storage and Azurite
        connection_string = (
            f"DefaultEndpointsProtocol=http;"
            f"AccountName={blob_config.account_name};"
            f"AccountKey={blob_config.account_key};"
            f"BlobEndpoint={blob_config.endpoint};"
        )
        
        self._client = BlobServiceClient.from_connection_string(connection_string)

    def write(self, data: pd.DataFrame) -> None:
        """Write DataFrame as Parquet to blob storage.
        
        Args:
            data: The DataFrame to write as Parquet.
            
        Raises:
            ValueError: If the client is not initialized.
            Exception: If writing the blob fails.
        """
        if self._client is None:
            raise ValueError("Client not initialized")
        
        blob_config = self._config.blob_storage
        container_client = self._client.get_container_client(blob_config.container_name)
        blob_client = container_client.get_blob_client(self._config.blob_path)
        
        # Convert DataFrame to Parquet in memory
        buffer = BytesIO()
        data.to_parquet(buffer, engine='pyarrow', index=False)
        buffer.seek(0)
        
        # Upload to blob storage
        blob_client.upload_blob(buffer.read(), overwrite=True)

    def close(self) -> None:
        """Close the blob service client and clean up resources."""
        if self._client is not None:
            self._client.close()
            self._client = None
