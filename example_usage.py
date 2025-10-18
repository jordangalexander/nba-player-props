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


def collect_season_data(
    season: str,
    player_ids: list[int],
    collector: DataCollector,
    include_playoffs: bool = True,
    batch_size: int = 12,
) -> pd.DataFrame:
    """
    Collect NBA data for all players in a specific season.

    Args:
        season: Season string (e.g., "2023-24")
        player_ids: List of player IDs to collect data for
        collector: DataCollector instance
        include_playoffs: Whether to include playoff games
        batch_size: Number of players to process per batch

    Returns:
        DataFrame with all player data for the season
    """
    logger.info(f"🏀 Collecting data for season {season}")
    logger.info(f"Players to process: {len(player_ids)}")
    logger.info(f"Batch size: {batch_size}")

    all_season_data = []
    total_games = 0
    failed_players = []

    # Process players in smaller batches
    for i in range(0, len(player_ids), batch_size):
        batch_end = min(i + batch_size, len(player_ids))
        batch_player_ids = player_ids[i:batch_end]
        batch_num = i // batch_size + 1
        total_batches = (len(player_ids) + batch_size - 1) // batch_size

        logger.info(
            f"📦 Processing batch {batch_num}/{total_batches}: "
            f"Players {i + 1}-{batch_end}"
        )

        try:
            # Collect data for this batch in the specific season
            batch_data = collector.collect_multiple_players(
                batch_player_ids, seasons=[season], include_playoffs=include_playoffs
            )

            if not batch_data.empty:
                all_season_data.append(batch_data)
                batch_games = len(batch_data)
                total_games += batch_games
                logger.info(f"✅ Batch {batch_num}: {batch_games} games collected")
            else:
                logger.warning(f"⚠️ Batch {batch_num}: No data collected")

            # Brief pause between batches to be API-friendly
            import time

            time.sleep(2.0)

        except Exception as e:
            logger.error(f"❌ Batch {batch_num} failed: {e}")
            failed_players.extend(batch_player_ids)
            continue

    # Combine all batch data for the season
    if all_season_data:
        season_df = pd.concat(all_season_data, ignore_index=True)
        season_df = season_df.sort_values(["PLAYER_ID", "GAME_DATE"])
        season_df = season_df.reset_index(drop=True)

        logger.info(f"🎉 Season {season} complete!")
        logger.info(f"📊 Total games: {len(season_df)}")
        logger.info(f"👥 Unique players: {season_df['PLAYER_ID'].nunique()}")

        if failed_players:
            logger.warning(f"⚠️ Failed players: {len(failed_players)}")

        return season_df
    else:
        logger.error(f"❌ No data collected for season {season}")
        return pd.DataFrame()


def collect_all_nba_data_by_season(
    start_year: int = 2010,
    include_playoffs: bool = True,
    batch_size: int = 12,
    save_progress: bool = True,
    output_dir: str = "season_data",
) -> dict[str, pd.DataFrame]:
    """
    Collect NBA data season-by-season, starting with most recent.

    Args:
        start_year: Starting year for data collection (default: 2010)
        include_playoffs: Whether to include playoff games
        batch_size: Number of players to process in each batch
        save_progress: Whether to save individual season files
        output_dir: Directory to save season files

    Returns:
        Dictionary mapping season names to DataFrames
    """
    logger.info("🚀 Starting season-by-season NBA data collection")
    logger.info(f"📅 Start year: {start_year}")
    logger.info(f"🏀 Include playoffs: {include_playoffs}")

    # Initialize collector with better timeout handling
    collector = DataCollector(rate_limit_delay=1.0)

    # Get seasons to collect (newest first for better value)
    all_seasons = collector.get_seasons_list(start_year=start_year)
    seasons = list(reversed(all_seasons))  # Start with most recent
    logger.info(f"📋 Seasons to collect: {seasons}")

    # Get all player IDs
    all_player_ids = get_all_historical_players(collector)
    if not all_player_ids:
        logger.warning("❌ No players found. Exiting.")
        return {}

    logger.info(f"👥 Total players to process: {len(all_player_ids)}")

    # Create output directory
    import os

    if save_progress and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"📁 Created output directory: {output_dir}")

    # Process each season
    season_results = {}
    successful_seasons = []
    failed_seasons = []

    for i, season in enumerate(seasons, 1):
        logger.info("=" * 60)
        logger.info(f"🎯 PROCESSING SEASON {season} ({i}/{len(seasons)})")
        logger.info("=" * 60)

        try:
            # Collect data for this season
            season_data = collect_season_data(
                season=season,
                player_ids=all_player_ids,
                collector=collector,
                include_playoffs=include_playoffs,
                batch_size=batch_size,
            )

            if not season_data.empty:
                season_results[season] = season_data
                successful_seasons.append(season)

                # Save individual season file
                if save_progress:
                    season_filename = f"{output_dir}/nba_data_{season}.csv"
                    season_data.to_csv(season_filename, index=False)
                    logger.info(f"💾 Saved: {season_filename}")

                # Log season summary
                games_count = len(season_data)
                players_count = season_data["PLAYER_ID"].nunique()
                logger.info(
                    f"✅ {season}: {games_count} games, {players_count} players"
                )

            else:
                logger.error(f"❌ No data collected for {season}")
                failed_seasons.append(season)

        except Exception as e:
            logger.error(f"💥 Season {season} failed: {e}")
            failed_seasons.append(season)
            continue

        # Brief pause between seasons
        if i < len(seasons):
            logger.info("⏸️ Brief pause between seasons...")
            import time

            time.sleep(5.0)

    # Final summary
    logger.info("=" * 60)
    logger.info("🏁 COLLECTION COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"✅ Successful seasons: {len(successful_seasons)}")
    logger.info(f"❌ Failed seasons: {len(failed_seasons)}")

    if successful_seasons:
        total_games = sum(len(df) for df in season_results.values())
        logger.info(f"📊 Total games collected: {total_games:,}")
        logger.info(f"📅 Seasons with data: {successful_seasons}")

    if failed_seasons:
        logger.warning(f"⚠️ Failed seasons: {failed_seasons}")

    return season_results


def create_combined_dataset(
    season_results: dict[str, pd.DataFrame],
    output_file: str = "nba_comprehensive_data.csv",
) -> pd.DataFrame:
    """
    Combine season-by-season results into a single dataset.

    Args:
        season_results: Dictionary of season DataFrames
        output_file: Output file for combined data

    Returns:
        Combined DataFrame with all seasons
    """
    if not season_results:
        logger.warning("⚠️ No season data to combine")
        return pd.DataFrame()

    logger.info("🔄 Combining all season data...")

    # Combine all seasons
    all_data_frames = list(season_results.values())
    combined_df = pd.concat(all_data_frames, ignore_index=True)

    # Add collection metadata
    combined_df["DATA_COLLECTED_AT"] = datetime.now()

    # Sort by player and date
    combined_df = combined_df.sort_values(["PLAYER_ID", "GAME_DATE"])
    combined_df = combined_df.reset_index(drop=True)

    # Save combined results
    combined_df.to_csv(output_file, index=False)
    logger.info(f"💾 Combined data saved to {output_file}")

    # Display summary stats
    display_summary_stats(combined_df)

    return combined_df

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
    batch_size: int = 12,
) -> bool:
    """Update NBA data collection using season-by-season approach.

    Args:
        start_year: Starting year for data collection
        include_playoffs: Whether to include playoff games
        output_file: Output CSV file name
        batch_size: Number of players per batch

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("🏀 NBA PLAYER DATA UPDATE - SEASON BY SEASON")
        logger.info("=" * 60)

        # Collect data season by season
        season_results = collect_all_nba_data_by_season(
            start_year=start_year,
            include_playoffs=include_playoffs,
            batch_size=batch_size,
            save_progress=True,
            output_dir="season_data",
        )

        if season_results:
            # Create combined dataset
            combined_data = create_combined_dataset(
                season_results, output_file=output_file
            )

            if not combined_data.empty:
                games_count = f"{len(combined_data):,}"
                seasons_count = len(season_results)
                logger.info("🎉 Update successful!")
                logger.info(f"📊 {games_count} games from {seasons_count} seasons")
                logger.info("🚀 Data is ready for analysis and modeling!")
                return True

        logger.error("❌ Update failed - no data collected.")
        return False

    except Exception as e:
        logger.error(f"💥 Update failed with error: {e}")
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
