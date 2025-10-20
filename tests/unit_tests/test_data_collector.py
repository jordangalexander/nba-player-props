"""Comprehensive test suite for the DataCollector class."""

import time
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from nba_player_props.data_collector.data_collector import DataCollector

#########################
# Fixtures
#########################


@pytest.fixture
def collector():
    """Create a DataCollector instance with faster rate limiting for tests."""
    return DataCollector(rate_limit_delay=0.1)


@pytest.fixture
def sample_active_players_df():
    """Sample active players DataFrame for testing."""
    return pd.DataFrame(
        {
            "PERSON_ID": [2544, 1628389, 203500],
            "DISPLAY_FIRST_LAST": ["LeBron James", "Luka Doncic", "Damian Lillard"],
            "ROSTERSTATUS": [1, 1, 1],
            "FROM_YEAR": ["2003-04", "2018-19", "2012-13"],
            "TO_YEAR": ["2023-24", "2023-24", "2023-24"],
        }
    )


@pytest.fixture
def sample_game_log_df():
    """Sample game log DataFrame for testing."""
    return pd.DataFrame(
        {
            "SEASON_ID": ["22023", "22023"],
            "PLAYER_ID": [2544, 2544],
            "GAME_ID": ["0022300001", "0022300002"],
            "GAME_DATE": ["2023-10-18", "2023-10-20"],
            "MATCHUP": ["LAL vs. DEN", "LAL @ PHX"],
            "WL": ["L", "W"],
            "MIN": [35, 38],
            "PTS": [21, 32],
            "REB": [8, 11],
            "AST": [5, 14],
            "STL": [0, 2],
            "BLK": [1, 0],
            "TOV": [4, 5],
            "PF": [1, 2],
            "PLUS_MINUS": [-10, 15],
        }
    )


@pytest.fixture
def mock_player_dict():
    """Mock player dictionary for static player data."""
    return [{"id": 2544, "full_name": "LeBron James"}]


@pytest.fixture(autouse=True)
def clear_cache(collector):
    """Clear cache before and after each test."""
    collector._active_players_cache = None
    collector._seasons_cache = None
    yield
    collector._active_players_cache = None
    collector._seasons_cache = None


#########################
# Initialization Tests
#########################


def test_collector_init_default_values():
    """Test DataCollector initialization with default values."""
    collector = DataCollector()
    assert collector.rate_limit_delay == 0.6
    assert collector._active_players_cache is None
    assert collector._seasons_cache is None


def test_collector_init_custom_values():
    """Test DataCollector initialization with custom values."""
    collector = DataCollector(rate_limit_delay=1.0)
    assert collector.rate_limit_delay == 1.0


#########################
# Active Players Tests
#########################


@patch("nba_player_props.data_collector.time.sleep")
@patch("nba_player_props.data_collector.commonallplayers.CommonAllPlayers")
def test_get_active_players_success(
    mock_common_all_players, mock_sleep, collector, sample_active_players_df
):
    """Test successful retrieval of active players."""
    # Mock the API response
    mock_instance = Mock()
    mock_instance.get_data_frames.return_value = [sample_active_players_df]
    mock_common_all_players.return_value = mock_instance

    result = collector.get_active_players("2023-24")

    # Verify API was called correctly
    mock_common_all_players.assert_called_once_with(
        is_only_current_season=1, season="2023-24"
    )
    mock_sleep.assert_called_once_with(0.1)

    # Verify result
    pd.testing.assert_frame_equal(result, sample_active_players_df)


@patch("nba_player_props.data_collector.time.sleep")
@patch("nba_player_props.data_collector.commonallplayers.CommonAllPlayers")
def test_get_active_players_caching(
    mock_common_all_players, mock_sleep, collector, sample_active_players_df
):
    """Test that active players results are cached properly."""
    mock_instance = Mock()
    mock_instance.get_data_frames.return_value = [sample_active_players_df]
    mock_common_all_players.return_value = mock_instance

    # First call
    result1 = collector.get_active_players("2023-24")
    # Second call should use cache
    result2 = collector.get_active_players("2023-24")

    # Verify caching works
    pd.testing.assert_frame_equal(result1, sample_active_players_df)
    pd.testing.assert_frame_equal(result2, sample_active_players_df)
    # Should only be called once due to caching
    assert mock_common_all_players.call_count == 1


@patch("nba_player_props.data_collector.time.sleep")
@patch("nba_player_props.data_collector.commonallplayers.CommonAllPlayers")
def test_get_active_players_api_error(mock_common_all_players, mock_sleep, collector):
    """Test handling of API errors when getting active players."""
    mock_common_all_players.side_effect = Exception("API Error")

    with patch("nba_player_props.data_collector.logger") as mock_logger:
        result = collector.get_active_players()

        # Should return empty DataFrame on error
        assert result.empty
        mock_logger.info.assert_called_once()


#########################
# Player ID Lookup Tests
#########################


@patch("nba_player_props.data_collector.players.find_players_by_full_name")
def test_get_player_id_by_name_success(mock_find_players, collector, mock_player_dict):
    """Test successful player ID retrieval by name."""
    mock_find_players.return_value = mock_player_dict

    result = collector.get_player_id_by_name("LeBron James")

    mock_find_players.assert_called_once_with("LeBron James")
    assert result == 2544


@patch("nba_player_props.data_collector.players.find_players_by_full_name")
def test_get_player_id_by_name_not_found(mock_find_players, collector):
    """Test player ID retrieval when player not found."""
    mock_find_players.return_value = []

    result = collector.get_player_id_by_name("Nonexistent Player")

    assert result is None


#########################
# Seasons List Tests
#########################


@patch("nba_player_props.data_collector.datetime")
def test_get_seasons_list_during_season(mock_datetime, collector):
    """Test seasons list generation during NBA season (after October)."""
    # Mock current date as December 2023 (during 2023-24 season)
    mock_now = Mock()
    mock_now.year = 2023
    mock_now.month = 12
    mock_datetime.now.return_value = mock_now

    result = collector.get_seasons_list(start_year=2020)

    expected = ["2020-21", "2021-22", "2022-23", "2023-24"]
    assert result == expected


@patch("nba_player_props.data_collector.datetime")
def test_get_seasons_list_before_season_start(mock_datetime, collector):
    """Test seasons list generation before NBA season starts."""
    # Mock current date as August 2023 (before 2023-24 season)
    mock_now = Mock()
    mock_now.year = 2023
    mock_now.month = 8
    mock_datetime.now.return_value = mock_now

    result = collector.get_seasons_list(start_year=2021)

    expected = ["2021-22", "2022-23"]  # Should not include 2023-24
    assert result == expected


@patch("nba_player_props.data_collector.datetime")
def test_get_seasons_list_caching(mock_datetime):
    """Test that seasons list is cached properly."""
    # Create collector without the autouse fixture interfering
    collector = DataCollector(rate_limit_delay=0.1)

    mock_now = Mock()
    mock_now.year = 2023
    mock_now.month = 12
    mock_datetime.now.return_value = mock_now

    result1 = collector.get_seasons_list(start_year=2020)
    result2 = collector.get_seasons_list(start_year=2020)

    expected = ["2020-21", "2021-22", "2022-23", "2023-24"]
    assert result1 == expected
    assert result2 == expected
    # First call makes 2 datetime.now() calls (year + month), second is cached
    assert mock_datetime.now.call_count == 2


def test_seasons_list_format():
    """Test that seasons list has correct format."""
    collector = DataCollector()
    seasons = collector.get_seasons_list(start_year=2020)

    for season in seasons:
        # Should be in format "YYYY-YY"
        assert len(season) == 7
        assert season[4] == "-"

        # Year should be consecutive
        start_year, end_year_suffix = season.split("-")
        expected_end = str(int(start_year) + 1)[2:]
        assert end_year_suffix == expected_end


#########################
# Player Season Stats Tests
#########################


@patch("nba_player_props.data_collector.time.sleep")
@patch("nba_player_props.data_collector.playergamelog.PlayerGameLog")
def test_get_player_season_stats_success(
    mock_player_game_log, mock_sleep, collector, sample_game_log_df
):
    """Test successful player season stats retrieval."""
    mock_instance = Mock()
    mock_instance.get_data_frames.return_value = [sample_game_log_df.copy()]
    mock_player_game_log.return_value = mock_instance

    result = collector.get_player_season_stats(2544, "2023-24", "Regular Season")

    # Verify API call
    mock_player_game_log.assert_called_once_with(
        player_id=2544, season="2023-24", season_type_all_star="Regular Season"
    )
    mock_sleep.assert_called_once_with(0.1)

    # Verify metadata columns were added
    assert "SEASON" in result.columns
    assert "SEASON_TYPE" in result.columns
    assert "PLAYER_ID" in result.columns
    assert result["SEASON"].iloc[0] == "2023-24"
    assert result["SEASON_TYPE"].iloc[0] == "Regular Season"
    assert result["PLAYER_ID"].iloc[0] == 2544


@patch("nba_player_props.data_collector.time.sleep")
@patch("nba_player_props.data_collector.playergamelog.PlayerGameLog")
def test_get_player_season_stats_empty_result(
    mock_player_game_log, mock_sleep, collector
):
    """Test handling of empty results from API."""
    mock_instance = Mock()
    mock_instance.get_data_frames.return_value = [pd.DataFrame()]
    mock_player_game_log.return_value = mock_instance

    result = collector.get_player_season_stats(2544, "2023-24")

    # Should return empty DataFrame
    assert result.empty


@patch("nba_player_props.data_collector.time.sleep")
@patch("nba_player_props.data_collector.playergamelog.PlayerGameLog")
def test_get_player_season_stats_api_error(mock_player_game_log, mock_sleep, collector):
    """Test handling of API errors."""
    mock_player_game_log.side_effect = Exception("API Error")

    with patch("nba_player_props.data_collector.logger") as mock_logger:
        result = collector.get_player_season_stats(2544, "2023-24")

        assert result is None
        mock_logger.info.assert_called_once()


#########################
# Player All Seasons Tests
#########################


@patch.object(DataCollector, "get_seasons_list")
@patch.object(DataCollector, "get_player_season_stats")
def test_get_player_all_seasons_success(
    mock_get_stats, mock_get_seasons, collector, sample_game_log_df
):
    """Test successful retrieval of player data across seasons."""
    mock_get_seasons.return_value = ["2022-23", "2023-24"]

    # Mock different game logs for different seasons
    df1 = sample_game_log_df.copy()
    df1["SEASON"] = "2022-23"
    df2 = sample_game_log_df.copy()
    df2["SEASON"] = "2023-24"

    # reg, playoffs, reg, playoffs
    mock_get_stats.side_effect = [df1, None, df2, pd.DataFrame()]

    result = collector.get_player_all_seasons(2544, include_playoffs=True)

    # Verify all API calls were made
    expected_calls = [
        (2544, "2022-23", "Regular Season"),
        (2544, "2022-23", "Playoffs"),
        (2544, "2023-24", "Regular Season"),
        (2544, "2023-24", "Playoffs"),
    ]
    actual_calls = [call.args for call in mock_get_stats.call_args_list]
    assert actual_calls == expected_calls

    # Verify result combines both seasons
    assert len(result) == 4  # 2 games from each season
    assert "GAME_DATE" in result.columns
    assert pd.api.types.is_datetime64_any_dtype(result["GAME_DATE"])


@patch.object(DataCollector, "get_seasons_list")
@patch.object(DataCollector, "get_player_season_stats")
def test_get_player_all_seasons_no_playoffs(
    mock_get_stats, mock_get_seasons, collector, sample_game_log_df
):
    """Test player data collection without playoffs."""
    mock_get_seasons.return_value = ["2023-24"]
    mock_get_stats.return_value = sample_game_log_df.copy()

    result = collector.get_player_all_seasons(2544, include_playoffs=False)

    # Should only call for regular season
    mock_get_stats.assert_called_once_with(2544, "2023-24", "Regular Season")
    assert len(result) == 2


@patch.object(DataCollector, "get_player_season_stats")
def test_get_player_all_seasons_custom_seasons(
    mock_get_stats, collector, sample_game_log_df
):
    """Test player data collection with custom seasons list."""
    custom_seasons = ["2021-22", "2022-23"]
    mock_get_stats.return_value = sample_game_log_df.copy()

    collector.get_player_all_seasons(
        2544, seasons=custom_seasons, include_playoffs=False
    )

    # Verify correct seasons were used
    expected_calls = [
        (2544, "2021-22", "Regular Season"),
        (2544, "2022-23", "Regular Season"),
    ]
    actual_calls = [call.args for call in mock_get_stats.call_args_list]
    assert actual_calls == expected_calls


@patch.object(DataCollector, "get_player_season_stats")
def test_get_player_all_seasons_no_data(mock_get_stats, collector):
    """Test handling when no data is returned."""
    mock_get_stats.return_value = None

    result = collector.get_player_all_seasons(2544, seasons=["2023-24"])

    assert result.empty


#########################
# Player Data by Name Tests
#########################


@patch.object(DataCollector, "get_player_id_by_name")
@patch.object(DataCollector, "get_player_all_seasons")
def test_get_player_data_by_name_success(
    mock_get_all_seasons, mock_get_id, collector, sample_game_log_df
):
    """Test successful player data retrieval by name."""
    mock_get_id.return_value = 2544
    mock_get_all_seasons.return_value = sample_game_log_df.copy()

    result = collector.get_player_data_by_name("LeBron James")

    mock_get_id.assert_called_once_with("LeBron James")
    mock_get_all_seasons.assert_called_once_with(2544, None, True)
    assert len(result) == 2


@patch.object(DataCollector, "get_player_id_by_name")
def test_get_player_data_by_name_not_found(mock_get_id, collector):
    """Test handling when player name is not found."""
    mock_get_id.return_value = None

    with patch("nba_player_props.data_collector.logger") as mock_logger:
        result = collector.get_player_data_by_name("Nonexistent Player")

        assert result.empty
        mock_logger.info.assert_called_once()


#########################
# Multiple Players Collection Tests
#########################


@patch.object(DataCollector, "get_seasons_list")
@patch.object(DataCollector, "get_player_all_seasons")
def test_collect_multiple_players_success(
    mock_get_all_seasons, mock_get_seasons, collector, sample_game_log_df
):
    """Test successful collection of multiple players' data."""
    mock_get_seasons.return_value = ["2023-24"]

    # Mock data for different players
    df1 = sample_game_log_df.copy()
    df1["PLAYER_ID"] = 2544
    df2 = sample_game_log_df.copy()
    df2["PLAYER_ID"] = 1628389

    mock_get_all_seasons.side_effect = [df1, df2]

    player_ids = [2544, 1628389]
    result = collector.collect_multiple_players(player_ids)

    # Verify all players were processed
    assert mock_get_all_seasons.call_count == 2
    assert len(result) == 4  # 2 games per player
    assert result["PLAYER_ID"].nunique() == 2


@patch.object(DataCollector, "get_seasons_list")
@patch.object(DataCollector, "get_player_all_seasons")
def test_collect_multiple_players_some_empty(
    mock_get_all_seasons, mock_get_seasons, collector, sample_game_log_df
):
    """Test collection when some players return no data."""
    mock_get_seasons.return_value = ["2023-24"]

    df1 = sample_game_log_df.copy()
    empty_df = pd.DataFrame()

    mock_get_all_seasons.side_effect = [df1, empty_df]

    player_ids = [2544, 1628389]
    result = collector.collect_multiple_players(player_ids)

    # Should only include data from the first player
    assert len(result) == 2
    assert result["PLAYER_ID"].nunique() == 1


@patch.object(DataCollector, "get_seasons_list")
@patch.object(DataCollector, "get_player_all_seasons")
def test_collect_multiple_players_all_empty(
    mock_get_all_seasons, mock_get_seasons, collector
):
    """Test collection when all players return no data."""
    mock_get_seasons.return_value = ["2023-24"]
    mock_get_all_seasons.return_value = pd.DataFrame()

    player_ids = [2544, 1628389]
    result = collector.collect_multiple_players(player_ids)

    assert result.empty


@patch.object(DataCollector, "get_player_all_seasons")
def test_collect_multiple_players_custom_seasons(
    mock_get_all_seasons, collector, sample_game_log_df
):
    """Test collection with custom seasons."""
    custom_seasons = ["2021-22", "2022-23"]
    mock_get_all_seasons.return_value = sample_game_log_df.copy()

    player_ids = [2544]
    result = collector.collect_multiple_players(
        player_ids, seasons=custom_seasons, include_playoffs=False
    )

    mock_get_all_seasons.assert_called_once_with(2544, custom_seasons, False)


def test_collect_multiple_players_empty_list(collector):
    """Test collection with empty player list."""
    result = collector.collect_multiple_players([])
    assert result.empty


#########################
# Integration Tests
#########################


def test_rate_limiting_respected():
    """Test that rate limiting delay is respected."""
    collector = DataCollector(rate_limit_delay=0.2)

    with patch(
        "nba_player_props.data_collector.playergamelog.PlayerGameLog"
    ) as mock_api:
        mock_instance = Mock()
        mock_instance.get_data_frames.return_value = [pd.DataFrame()]
        mock_api.return_value = mock_instance

        start_time = time.time()
        collector.get_player_season_stats(2544, "2023-24")
        elapsed = time.time() - start_time

        # Should take at least the rate limit delay
        assert elapsed >= 0.2
