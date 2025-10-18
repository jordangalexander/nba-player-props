"""Test configuration and fixtures."""

import pytest
import pandas as pd
from typing import Generator


@pytest.fixture
def sample_game_logs() -> pd.DataFrame:
    """Sample game logs for testing."""
    return pd.DataFrame({
        "game_id": ["001", "002", "003"],
        "date": ["2023-10-15", "2023-10-17", "2023-10-19"],
        "opponent": ["LAL", "GSW", "BOS"],
        "points": [25, 30, 18],
        "rebounds": [8, 6, 12],
        "assists": [5, 7, 4],
        "minutes": [35, 38, 32]
    })


@pytest.fixture
def sample_player_data() -> pd.DataFrame:
    """Sample player data for testing."""
    return pd.DataFrame({
        "player_id": [1, 1, 1],
        "season": ["2023-24", "2023-24", "2023-24"],
        "avg_points": [24.5, 24.8, 25.0],
        "avg_rebounds": [7.2, 7.1, 7.3],
        "avg_assists": [5.8, 6.0, 5.9]
    })