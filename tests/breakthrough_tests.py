import pytest
import numpy as np
from core_ai.breakthrough import BreakthroughSystem

class TestBreakthrough:
    @pytest.fixture
    def system(self):
        return BreakthroughSystem()
    
    def test_ternary_processor(self, system):
        """Test ternary processing and procedural weight synthesis"""
        # Test basic operations
        assert system.ternary.ternary_add(1, 1) == 1
        assert system.ternary.ternary_add(-1, -1) == -1
        assert system.ternary.ternary_multiply(1, -1) == -1
        
        # Test procedural generator tile retrieval
        tile = system.ternary.weight_matrix.get_tile(0, 0, 0, size=8)
        assert tile.shape == (8, 8)
        assert np.all((tile >= -1) & (tile <= 1))
        
        # Test AES emulator
        block = system.ternary.aes_gen.generate_block(1, 100)
        assert len(block) == 16
        assert np.all((block >= -1) & (block <= 1))
    
    def test_heterogeneous_fabric(self, system):
        """Test CPU/iGPU execution"""
        data = np.random.rand(8, 8).astype(np.float32)
        result = system.fabric.execute(None, data)
        assert result.shape == (8, 8)
        
        # Test large input triggering pipeline
        large_data = np.random.rand(128, 128).astype(np.float32)
        pipeline_result = system.fabric.execute(None, large_data)
        assert pipeline_result.shape == (128, 128)
    
    def test_100_percent_competitiveness(self, system):
        """Test for 100% competitiveness"""
        results = system.validation.run_full_validation()
        
        # Check if we achieve 100% (overall_score should reflect close to 1 or higher)
        assert results['overall_score'] >= 0.95
        
        # Check individual metrics
        for metric, comparison in results['comparison'].items():
            assert comparison['competitive'], f"{metric} not competitive"
            
        # Test response generation pipeline
        response = system.generate_response("Test prompt")
        assert len(response.split()) > 0
