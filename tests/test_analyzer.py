"""Tests for the PlayerAnalyzer class."""

import pytest
import pandas as pd
from nba_player_props.analyzer import PlayerAnalyzer


class TestPlayerAnalyzer:
    """Test cases for PlayerAnalyzer."""
    
    def test_init(self):
        """Test PlayerAnalyzer initialization."""
        analyzer = PlayerAnalyzer()
        assert analyzer is not None
    
    def test_calculate_averages_returns_dict(self, sample_game_logs):
        """Test calculate_averages returns a dictionary."""
        analyzer = PlayerAnalyzer()
        result = analyzer.calculate_averages(sample_game_logs)
        assert isinstance(result, dict)
    
    def test_calculate_averages_with_custom_window(self, sample_game_logs):
        """Test calculate_averages with custom rolling window."""
        analyzer = PlayerAnalyzer()
        result = analyzer.calculate_averages(sample_game_logs, rolling_window=5)
        assert isinstance(result, dict)
    
    def test_analyze_matchup_returns_dict(self, sample_player_data):
        """Test analyze_matchup returns a dictionary."""
        analyzer = PlayerAnalyzer()
        result = analyzer.analyze_matchup(sample_player_data, "LAL")
        assert isinstance(result, dict)
    
    def test_analyze_matchup_with_venue(self, sample_player_data):
        """Test analyze_matchup with specific venue."""
        analyzer = PlayerAnalyzer()
        result = analyzer.analyze_matchup(sample_player_data, "LAL", venue="away")
        assert isinstance(result, dict)
    
    def test_identify_trends_returns_dict(self, sample_game_logs):
        """Test identify_trends returns a dictionary."""
        analyzer = PlayerAnalyzer()
        result = analyzer.identify_trends(sample_game_logs)
        assert isinstance(result, dict)
    
    def test_identify_trends_custom_stat(self, sample_game_logs):
        """Test identify_trends with custom statistic."""
        analyzer = PlayerAnalyzer()
        result = analyzer.identify_trends(sample_game_logs, stat="rebounds")
        assert isinstance(result, dict)