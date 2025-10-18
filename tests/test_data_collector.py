"""Tests for the DataCollector class."""

import pytest
import pandas as pd
from datetime import date
from nba_player_props.data_collector import DataCollector


class TestDataCollector:
    """Test cases for DataCollector."""
    
    def test_init(self):
        """Test DataCollector initialization."""
        collector = DataCollector()
        assert collector.rate_limit_delay == 0.6
        
    def test_init_with_custom_delay(self):
        """Test DataCollector initialization with custom delay."""
        collector = DataCollector(rate_limit_delay=1.0)
        assert collector.rate_limit_delay == 1.0
    
    def test_get_player_id_valid_player(self):
        """Test get_player_id with a known player."""
        collector = DataCollector()
        # Test with LeBron James - should return his player ID
        player_id = collector.get_player_id("LeBron James")
        assert player_id is not None
        assert isinstance(player_id, int)
    
    def test_get_player_id_invalid_player(self):
        """Test get_player_id with non-existent player."""
        collector = DataCollector()
        player_id = collector.get_player_id("Non Existent Player")
        assert player_id is None
    
    def test_get_player_box_scores_since_2015_returns_dataframe(self):
        """Test that get_player_box_scores_since_2015 returns a DataFrame."""
        collector = DataCollector()
        # Use a specific end date to limit data and speed up test
        end_date = date(2016, 1, 1)
        result = collector.get_player_box_scores_since_2015(
            "LeBron James",
            end_date=end_date
        )
        assert isinstance(result, pd.DataFrame)
    
    def test_generate_seasons_until_date(self):
        """Test _generate_seasons_until_date method."""
        collector = DataCollector()
        end_date = date(2017, 6, 30)
        seasons = collector._generate_seasons_until_date(end_date)
        
        assert "2015-16" in seasons
        assert "2016-17" in seasons
        assert len(seasons) >= 2