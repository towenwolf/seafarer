"""Blob CSV Reader source port implementation."""

from io import BytesIO
from typing import Optional

import pandas as pd
from azure.storage.blob import BlobServiceClient

from seafarer.config import SourcePortConfig
from seafarer.ports.base import SourcePort


class BlobCSVReader(SourcePort):
    """Source port that reads CSV files from Azure Blob Storage.
    
    This port is configured via endpoint and credentials only, with no
    emulator-specific logic. It works with both Azure Blob Storage and
    compatible blob storage emulators like Azurite.
    """

    def __init__(self, config: SourcePortConfig) -> None:
        """Initialize the BlobCSVReader.
        
        Args:
            config: Configuration for the source port including blob storage
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

    def read(self) -> pd.DataFrame:
        """Read CSV data from blob storage.
        
        Returns:
            pd.DataFrame: The CSV data as a pandas DataFrame.
            
        Raises:
            ValueError: If the client is not initialized.
            Exception: If reading the blob fails.
        """
        if self._client is None:
            raise ValueError("Client not initialized")
        
        blob_config = self._config.blob_storage
        container_client = self._client.get_container_client(blob_config.container_name)
        blob_client = container_client.get_blob_client(self._config.blob_path)
        
        # Download blob content
        blob_data = blob_client.download_blob()
        blob_bytes = blob_data.readall()
        
        # Parse CSV from bytes
        df = pd.read_csv(BytesIO(blob_bytes))
        
        return df

    def close(self) -> None:
        """Close the blob service client and clean up resources."""
        if self._client is not None:
            self._client.close()
            self._client = None
