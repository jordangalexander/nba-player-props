"""Tests for the DataCollector class."""

import pytest
import pandas as pd
from nba_player_props.data_collector import DataCollector


class TestDataCollector:
    """Test cases for DataCollector."""
    
    def test_init(self):
        """Test DataCollector initialization."""
        collector = DataCollector()
        assert collector.base_url == "https://stats.nba.com/stats"
        assert "User-Agent" in collector.headers
    
    def test_get_player_stats_returns_dataframe(self):
        """Test get_player_stats returns a DataFrame."""
        collector = DataCollector()
        result = collector.get_player_stats(player_id=123, season="2023-24")
        assert isinstance(result, pd.DataFrame)
    
    def test_get_game_logs_returns_dataframe(self):
        """Test get_game_logs returns a DataFrame."""
        collector = DataCollector()
        result = collector.get_game_logs(player_id=123, season="2023-24")
        assert isinstance(result, pd.DataFrame)
    
    def test_get_player_stats_with_default_season(self):
        """Test get_player_stats with default season parameter."""
        collector = DataCollector()
        result = collector.get_player_stats(player_id=123)
        assert isinstance(result, pd.DataFrame)
    
    def test_get_game_logs_with_default_season(self):
        """Test get_game_logs with default season parameter."""
        collector = DataCollector()
        result = collector.get_game_logs(player_id=123)
        assert isinstance(result, pd.DataFrame)