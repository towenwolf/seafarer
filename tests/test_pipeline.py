"""Tests for core pipeline."""

from unittest.mock import MagicMock

from seafarer.core.pipeline import Pipeline
from seafarer.ports.base import SinkPort, SourcePort


def test_pipeline_run():
    """Test pipeline execution without transformation."""
    
    class MockSource(SourcePort):
        def read(self):
            yield "data1"
            yield "data2"
        
        def close(self):
            self.closed = True
    
    class MockSink(SinkPort):
        def __init__(self):
            self.written_data = []
            
        def write(self, data):
            self.written_data.append(data)
        
        def close(self):
            self.closed = True
    
    source = MockSource()
    sink = MockSink()
    pipeline = Pipeline(source=source, sink=sink)
    
    pipeline.run()
    
    assert sink.written_data == ["data1", "data2"]
    assert source.closed
    assert sink.closed


def test_pipeline_run_with_transform():
    """Test pipeline execution with transformation."""
    
    class MockSource(SourcePort):
        def read(self):
            yield 1
            yield 2
        
        def close(self):
            pass
    
    class MockSink(SinkPort):
        def __init__(self):
            self.written_data = []
            
        def write(self, data):
            self.written_data.append(data)
        
        def close(self):
            pass
    
    def transform_fn(data):
        return data * 2
    
    source = MockSource()
    sink = MockSink()
    pipeline = Pipeline(source=source, sink=sink, transform=transform_fn)
    
    pipeline.run()
    
    assert sink.written_data == [2, 4]
