"""
NBA Player Data Update Module

This module provides functionality to collect and update NBA player box score data.
Designed to be executed as a script or imported as a module.
"""

import logging
from datetime import datetime

import pandas as pd

from nba_player_props.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("nba_data_collection.log"),  # File output
    ],
)

logger = logging.getLogger(__name__)


def get_all_historical_players(collector: DataCollector) -> list[int]:
    """Get all player IDs who have played since 2010.

    Args:
        collector: DataCollector instance

    Returns:
        List of unique player IDs
    """
    logger.info("Fetching all historical players...")

    # Collect active players from recent seasons for comprehensive list
    all_player_ids = set()

    # Get players from recent seasons (they cover most historical players too)
    recent_seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

    for season in recent_seasons:
        try:
            logger.info(f"Getting active players from {season}...")
            active_players = collector.get_active_players(season)

            if not active_players.empty:
                season_player_ids = active_players["PERSON_ID"].tolist()
                all_player_ids.update(season_player_ids)
                player_count = len(season_player_ids)
                logger.info(f"Found {player_count} players in {season}")

        except Exception as e:
            logger.error(f"Error getting players for {season}: {e}")
            continue

    player_list = list(all_player_ids)
    logger.info(f"Total unique players found: {len(player_list)}")
    return player_list


def collect_all_nba_data(
    start_year: int = 2010,
    include_playoffs: bool = True,
    batch_size: int = 25,
    save_progress: bool = True,
    output_file: str = "nba_comprehensive_data.csv",
) -> pd.DataFrame:
    """
    Collect comprehensive NBA player box score data from start_year to present.

    Args:
        start_year: Starting year for data collection (default: 2010)
        include_playoffs: Whether to include playoff games
        batch_size: Number of players to process in each batch
        save_progress: Whether to save progress periodically
        output_file: File name to save results

    Returns:
        DataFrame with all collected player box score data
    """
    logger.info(f"Starting NBA data collection from {start_year}...")

    # Initialize collector with longer delay for stability
    collector = DataCollector(rate_limit_delay=0.8)

    # Get seasons to collect
    seasons = collector.get_seasons_list(start_year=start_year)
    logger.info(f"Seasons to collect: {seasons}")

    # Get all player IDs
    all_player_ids = get_all_historical_players(collector)

    if not all_player_ids:
        logger.warning("No players found. Exiting.")
        return pd.DataFrame()

    logger.info(
        f"Will collect data for {len(all_player_ids)} players "
        f"across {len(seasons)} seasons"
    )
    calls_per_player = len(seasons) * (2 if include_playoffs else 1)
    total_calls = len(all_player_ids) * calls_per_player
    logger.info(f"Estimated total API calls: {total_calls}")

    # Collect data in batches
    all_data_frames = []
    total_games = 0

    for i in range(0, len(all_player_ids), batch_size):
        batch_end = min(i + batch_size, len(all_player_ids))
        batch_player_ids = all_player_ids[i:batch_end]

        logger.info(
            f"Processing batch {i // batch_size + 1}: "
            f"Players {i + 1}-{batch_end} of {len(all_player_ids)}"
        )

        try:
            batch_data = collector.collect_multiple_players(
                batch_player_ids, seasons=seasons, include_playoffs=include_playoffs
            )

            if not batch_data.empty:
                all_data_frames.append(batch_data)
                batch_games = len(batch_data)
                total_games += batch_games
                logger.info(f"Batch collected: {batch_games} games")
                logger.info(f"Total games so far: {total_games}")

                # Save progress periodically
                if save_progress and len(all_data_frames) % 5 == 0:
                    temp_df = pd.concat(all_data_frames, ignore_index=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    temp_filename = f"progress_{timestamp}.csv"
                    temp_df.to_csv(temp_filename, index=False)
                    logger.info(f"Progress saved to {temp_filename}")
            else:
                logger.warning("No data collected for this batch")

        except Exception as e:
            logger.error(f"Error processing batch {i // batch_size + 1}: {e}")
            continue

    # Combine all data
    if all_data_frames:
        logger.info("Combining all collected data...")
        final_df = pd.concat(all_data_frames, ignore_index=True)

        # Add collection metadata
        final_df["DATA_COLLECTED_AT"] = datetime.now()

        # Sort by player and date
        final_df = final_df.sort_values(["PLAYER_ID", "GAME_DATE"])
        final_df = final_df.reset_index(drop=True)

        logger.info("=== COLLECTION COMPLETE ===")
        logger.info(f"Total games collected: {len(final_df)}")
        logger.info(f"Unique players: {final_df['PLAYER_ID'].nunique()}")
        logger.info(f"Seasons covered: {sorted(final_df['SEASON'].unique())}")
        date_min = final_df["GAME_DATE"].min()
        date_max = final_df["GAME_DATE"].max()
        logger.info(f"Date range: {date_min} to {date_max}")

        # Save final results
        final_df.to_csv(output_file, index=False)
        logger.info(f"Results saved to {output_file}")

        # Display sample statistics
        display_summary_stats(final_df)

        return final_df
    else:
        logger.warning("No data was collected.")
        return pd.DataFrame()


def display_summary_stats(df: pd.DataFrame) -> None:
    """Display summary statistics of the collected data."""
    logger.info("=== SUMMARY STATISTICS ===")

    # Overall stats
    logger.info(f"Total games: {len(df):,}")
    logger.info(f"Unique players: {df['PLAYER_ID'].nunique():,}")

    # Games by season
    games_by_season = df["SEASON"].value_counts().sort_index()
    logger.info("Games by season:")
    for season, count in games_by_season.items():
        logger.info(f"  {season}: {count:,} games")

    # Top scorers
    if "PTS" in df.columns:
        cols = ["GAME_DATE", "PLAYER_ID", "PTS", "SEASON"]
        top_games = df.nlargest(10, "PTS")[cols]
        logger.info("Top 10 scoring games:")
        for _, game in top_games.iterrows():
            pts = game["PTS"]
            player_id = game["PLAYER_ID"]
            season = game["SEASON"]
            logger.info(f"  Player {player_id}: {pts} pts ({season})")


def update_nba_data(
    start_year: int = 2010,
    include_playoffs: bool = True,
    output_file: str = "nba_comprehensive_data.csv",
) -> bool:
    """Update NBA data collection.

    Args:
        start_year: Starting year for data collection
        include_playoffs: Whether to include playoff games
        output_file: Output CSV file name

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("NBA PLAYER DATA UPDATE")
        logger.info("=" * 60)

        all_data = collect_all_nba_data(
            start_year=start_year,
            include_playoffs=include_playoffs,
            batch_size=25,
            save_progress=True,
            output_file=output_file,
        )

        if not all_data.empty:
            games_count = f"{len(all_data):,}"
            logger.info(f"✅ Update successful! {games_count} games collected.")
            logger.info("Data is ready for analysis and modeling.")
            return True
        else:
            logger.error("❌ Update failed - no data collected.")
            return False

    except Exception as e:
        logger.error(f"❌ Update failed with error: {e}")
        return False


def collect_sample_data(
    num_players: int = 5, seasons: list[str] = None
) -> pd.DataFrame:
    """Collect a small sample of data for testing/demo purposes.

    Args:
        num_players: Number of players to collect data for
        seasons: List of seasons to collect (defaults to ["2023-24"])

    Returns:
        DataFrame with sample data
    """
    if seasons is None:
        seasons = ["2023-24"]

    logger.info(f"Collecting sample data for {num_players} players...")

    collector = DataCollector()

    # Get active players
    active_players = collector.get_active_players()
    if active_players.empty:
        logger.warning("No active players found")
        return pd.DataFrame()

    # Take requested number of players
    sample_player_ids = active_players["PERSON_ID"].head(num_players).tolist()

    # Get data for specified seasons
    sample_data = collector.collect_multiple_players(
        sample_player_ids, seasons=seasons, include_playoffs=False
    )

    if not sample_data.empty:
        logger.info(f"Sample collection successful: {len(sample_data)} games")

    return sample_data


def main():
    """Main execution function for interactive use."""
    import sys

    if len(sys.argv) > 1:
        # Command line execution
        if sys.argv[1] == "update":
            update_nba_data()
        elif sys.argv[1] == "sample":
            collect_sample_data()
        else:
            logger.info("Usage: python example_usage.py [update|sample]")
    else:
        # Interactive mode
        logger.info("NBA Data Collection Module")
        logger.info("Available commands:")
        logger.info("  python example_usage.py update  - Full data update")
        logger.info("  python example_usage.py sample  - Collect sample data")

        response = input("\nRun full update? (y/N): ").lower().strip()
        if response == "y":
            update_nba_data()
        else:
            logger.info("Running sample collection instead...")
            sample_data = collect_sample_data()
            if not sample_data.empty:
                logger.info(f"Sample collected: {len(sample_data)} games")


if __name__ == "__main__":
    main()
