"""Tests for the PropPredictor class."""

import pytest
import pandas as pd
from nba_player_props.predictor import PropPredictor


class TestPropPredictor:
    """Test cases for PropPredictor."""
    
    def test_init(self):
        """Test PropPredictor initialization."""
        predictor = PropPredictor()
        assert predictor.models == {}
        assert predictor.is_trained is False
    
    def test_prepare_features_returns_dataframe(self, sample_player_data):
        """Test prepare_features returns a DataFrame."""
        predictor = PropPredictor()
        result = predictor.prepare_features(sample_player_data)
        assert isinstance(result, pd.DataFrame)
    
    def test_train_model_updates_state(self, sample_player_data):
        """Test train_model updates predictor state."""
        predictor = PropPredictor()
        predictor.train_model(sample_player_data, "points")
        assert "points" in predictor.models
        assert predictor.is_trained is True
    
    def test_predict_prop_returns_tuple(self, sample_player_data):
        """Test predict_prop returns tuple of probabilities."""
        predictor = PropPredictor()
        result = predictor.predict_prop(sample_player_data, 25.5)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert 0 <= result[0] <= 1
        assert 0 <= result[1] <= 1
    
    def test_predict_prop_with_custom_stat(self, sample_player_data):
        """Test predict_prop with custom statistic."""
        predictor = PropPredictor()
        result = predictor.predict_prop(sample_player_data, 7.5, stat="rebounds")
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_get_recommendation_returns_dict(self, sample_player_data):
        """Test get_recommendation returns dictionary."""
        predictor = PropPredictor()
        result = predictor.get_recommendation(sample_player_data, 25.5)
        assert isinstance(result, dict)
        assert "recommendation" in result
        assert "confidence" in result
        assert "reasoning" in result
    
    def test_get_recommendation_with_custom_threshold(self, sample_player_data):
        """Test get_recommendation with custom confidence threshold."""
        predictor = PropPredictor()
        result = predictor.get_recommendation(
            sample_player_data, 25.5, confidence_threshold=0.8
        )
        assert isinstance(result, dict)
        assert "recommendation" in result