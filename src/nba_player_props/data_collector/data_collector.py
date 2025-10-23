"""Data collection module for NBA player box score data."""

import logging
import time
from datetime import datetime

import pandas as pd
from nba_api.stats.endpoints import commonallplayers, playergamelog
from nba_api.stats.static import players

# Set up logger
logger = logging.getLogger(__name__)


class DataCollector:
    """Collects NBA player box score data using nba-api."""

    def __init__(self, rate_limit_delay: float = 0.6) -> None:
        """Initialize the data collector.

        Args:
            rate_limit_delay: Delay between API calls to avoid rate limiting
        """
        self.rate_limit_delay = rate_limit_delay
        self._active_players_cache = None
        self._seasons_cache = None

    def get_active_players(self, season: str = "2024-25") -> pd.DataFrame:
        """Get all active NBA players for a given season.

        Args:
            season: Season in format "2024-25"

        Returns:
            DataFrame with active players (PERSON_ID, DISPLAY_FIRST_LAST, etc.)
        """
        if self._active_players_cache is not None:
            return self._active_players_cache

        try:
            time.sleep(self.rate_limit_delay)
            all_players = commonallplayers.CommonAllPlayers(
                is_only_current_season=1, season=season
            )
            self._active_players_cache = all_players.get_data_frames()[0]
            return self._active_players_cache
        except Exception as e:
            logger.info(f"Error fetching active players: {e}")
            return pd.DataFrame()

    def get_player_id_by_name(self, player_name: str) -> int | None:
        """Get NBA player ID from player name using static data.

        Args:
            player_name: Full name of the player (e.g., "LeBron James")

        Returns:
            Player ID if found, None otherwise
        """
        player_dict = players.find_players_by_full_name(player_name)
        if player_dict:
            return player_dict[0]["id"]
        return None

    def get_player_name_by_id(self, player_id: int) -> str | None:
        """Get NBA player name from player ID using static data.

        Args:
            player_id: NBA player ID

        Returns:
            Player full name if found, None otherwise
        """
        try:
            player_info = players.find_player_by_id(player_id)
            if player_info:
                return player_info["full_name"]
        except Exception:
            pass
        return None

    def get_seasons_list(self, start_year: int = 2010) -> list[str]:
        """Get list of NBA seasons from start_year to current season.

        Args:
            start_year: Starting year (e.g., 2010 for 2010-11 season)

        Returns:
            List of season strings ["2015-16", "2016-17", ...]
        """
        if self._seasons_cache is not None:
            return self._seasons_cache

        current_year = datetime.now().year
        current_month = datetime.now().month

        # NBA season starts in October, so if we're before October,
        # the current season is the previous year
        if current_month < 10:
            current_year -= 1

        seasons = []
        for year in range(start_year, current_year + 1):
            seasons.append(f"{year}-{str(year + 1)[2:]}")

        self._seasons_cache = seasons
        return seasons

    def get_player_season_stats(
        self, player_id: int, season: str, season_type: str = "Regular Season"
    ) -> pd.DataFrame | None:
        """Get player box scores for a specific season.

        Args:
            player_id: NBA player ID
            season: Season in format "2023-24"
            season_type: "Regular Season" or "Playoffs"

        Returns:
            DataFrame with player box scores or None if error
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(self.rate_limit_delay)

                game_log = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=season,
                    season_type_all_star=season_type,
                    timeout=60,  # Increase timeout to 60 seconds
                )

                df = game_log.get_data_frames()[0]

                if not df.empty:
                    # Add metadata columns
                    df["SEASON"] = season
                    df["SEASON_TYPE"] = season_type
                    df["PLAYER_ID"] = player_id

                    # Add player name for easier analysis
                    player_name = self.get_player_name_by_id(player_id)
                    df["PLAYER_NAME"] = (
                        player_name if player_name else f"Player_{player_id}"
                    )

                return df

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.warning(
                        f"Attempt {attempt + 1} failed for player {player_id}, "
                        f"season {season} ({season_type}). "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    error_msg = (
                        f"Error fetching {season_type} data for "
                        f"player {player_id}, season {season}: {e}"
                    )
                    logger.info(error_msg)
                    return None

    def get_player_all_seasons(
        self,
        player_id: int,
        seasons: list[str] | None = None,
        include_playoffs: bool = True,
    ) -> pd.DataFrame:
        """Get player box scores for multiple seasons efficiently.

        Args:
            player_id: NBA player ID
            seasons: List of seasons to collect. If None, uses all since 2015
            include_playoffs: Whether to include playoff games

        Returns:
            DataFrame with all player box scores across seasons
        """
        if seasons is None:
            seasons = self.get_seasons_list()

        all_games = []

        for season in seasons:
            logger.info(f"Fetching {season} regular season for player {player_id}...")

            # Get regular season
            regular_df = self.get_player_season_stats(
                player_id, season, "Regular Season"
            )
            if regular_df is not None and not regular_df.empty:
                all_games.append(regular_df)

            # Get playoffs if requested
            if include_playoffs:
                playoff_df = self.get_player_season_stats(player_id, season, "Playoffs")
                if playoff_df is not None and not playoff_df.empty:
                    all_games.append(playoff_df)

        # Combine and clean data
        if all_games:
            combined_df = pd.concat(all_games, ignore_index=True)
            # Use more flexible date parsing to handle different formats
            combined_df["GAME_DATE"] = pd.to_datetime(
                combined_df["GAME_DATE"], errors="coerce"
            )
            combined_df = combined_df.sort_values("GAME_DATE")
            combined_df = combined_df.reset_index(drop=True)
            return combined_df

        return pd.DataFrame()

    def get_player_data_by_name(
        self,
        player_name: str,
        seasons: list[str] | None = None,
        include_playoffs: bool = True,
    ) -> pd.DataFrame:
        """Get player data by name (convenience method).

        Args:
            player_name: Full player name
            seasons: List of seasons to collect
            include_playoffs: Whether to include playoff games

        Returns:
            DataFrame with player box scores
        """
        player_id = self.get_player_id_by_name(player_name)
        if not player_id:
            logger.info(f"Player '{player_name}' not found")
            return pd.DataFrame()

        return self.get_player_all_seasons(player_id, seasons, include_playoffs)

    def collect_multiple_players(
        self,
        player_ids: list[int],
        seasons: list[str] | None = None,
        include_playoffs: bool = True,
    ) -> pd.DataFrame:
        """Efficiently collect data for multiple players.

        Args:
            player_ids: List of NBA player IDs
            seasons: List of seasons to collect
            include_playoffs: Whether to include playoff games

        Returns:
            DataFrame with box scores for all players
        """
        if seasons is None:
            seasons = self.get_seasons_list()

        all_player_data = []

        logger.info(
            f"Collecting data for {len(player_ids)} players "
            f"across {len(seasons)} seasons..."
        )

        for i, player_id in enumerate(player_ids, 1):
            logger.info(f"Processing player {i}/{len(player_ids)}: ID {player_id}")

            player_df = self.get_player_all_seasons(
                player_id, seasons, include_playoffs
            )

            if not player_df.empty:
                all_player_data.append(player_df)

        # Combine all players
        if all_player_data:
            final_df = pd.concat(all_player_data, ignore_index=True)
            logger.info(f"Total games collected: {len(final_df)}")
            return final_df

        return pd.DataFrame()
