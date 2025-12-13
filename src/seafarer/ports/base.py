"""Base port interfaces for seafarer."""

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class SourcePort(ABC):
    """Abstract base class for source ports.
    
    Source ports read data from external systems and provide it to the pipeline.
    """

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """Read data from the source.
        
        Returns:
            pd.DataFrame: The data read from the source.
            
        Raises:
            Exception: If reading fails.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection and clean up resources."""
        pass


class SinkPort(ABC):
    """Abstract base class for sink ports.
    
    Sink ports write data from the pipeline to external systems.
    """

    @abstractmethod
    def write(self, data: pd.DataFrame) -> None:
        """Write data to the sink.
        
        Args:
            data: The data to write to the sink.
            
        Raises:
            Exception: If writing fails.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection and clean up resources."""
        pass
