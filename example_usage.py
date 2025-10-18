"""
Comprehensive NBA Player Data Collection Script

This script collects box score data for all NBA players from 2010-11 season
to the current season and stores the results in a DataFrame.
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
    print("Fetching all historical players...")

    # Collect active players from recent seasons for comprehensive list
    all_player_ids = set()

    # Get players from recent seasons (they cover most historical players too)
    recent_seasons = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]

    for season in recent_seasons:
        try:
            print(f"Getting active players from {season}...")
            active_players = collector.get_active_players(season)

            if not active_players.empty:
                season_player_ids = active_players["PERSON_ID"].tolist()
                all_player_ids.update(season_player_ids)
                print(f"Found {len(season_player_ids)} players in {season}")

        except Exception as e:
            print(f"Error getting players for {season}: {e}")
            continue

    player_list = list(all_player_ids)
    print(f"Total unique players found: {len(player_list)}")
    return player_list


def collect_all_nba_data(
    start_year: int = 2010,
    include_playoffs: bool = True,
    batch_size: int = 50,
    save_progress: bool = True,
    output_file: str = "nba_all_players_data.csv",
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
    print(f"Starting comprehensive NBA data collection from {start_year}...")

    # Initialize collector with longer delay for stability
    collector = DataCollector(rate_limit_delay=0.8)

    # Get seasons to collect
    seasons = collector.get_seasons_list(start_year=start_year)
    print(f"Seasons to collect: {seasons}")

    # Get all player IDs
    all_player_ids = get_all_historical_players(collector)

    if not all_player_ids:
        print("No players found. Exiting.")
        return pd.DataFrame()

    print(
        f"Will collect data for {len(all_player_ids)} players "
        f"across {len(seasons)} seasons"
    )
    calls_per_player = len(seasons) * (2 if include_playoffs else 1)
    total_calls = len(all_player_ids) * calls_per_player
    print(f"Estimated total API calls: {total_calls}")

    # Collect data in batches
    all_data_frames = []
    total_games = 0

    for i in range(0, len(all_player_ids), batch_size):
        batch_end = min(i + batch_size, len(all_player_ids))
        batch_player_ids = all_player_ids[i:batch_end]

        print(
            f"\nProcessing batch {i // batch_size + 1}: "
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
                print(f"Batch collected: {batch_games} games")
                print(f"Total games so far: {total_games}")

                # Save progress periodically
                if save_progress and len(all_data_frames) % 5 == 0:
                    temp_df = pd.concat(all_data_frames, ignore_index=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    temp_filename = f"progress_{timestamp}.csv"
                    temp_df.to_csv(temp_filename, index=False)
                    print(f"Progress saved to {temp_filename}")
            else:
                print("No data collected for this batch")

        except Exception as e:
            print(f"Error processing batch {i // batch_size + 1}: {e}")
            continue

    # Combine all data
    if all_data_frames:
        print("\nCombining all collected data...")
        final_df = pd.concat(all_data_frames, ignore_index=True)

        # Add collection metadata
        final_df["DATA_COLLECTED_AT"] = datetime.now()

        # Sort by player and date
        final_df = final_df.sort_values(["PLAYER_ID", "GAME_DATE"])
        final_df = final_df.reset_index(drop=True)

        print("\n=== COLLECTION COMPLETE ===")
        print(f"Total games collected: {len(final_df)}")
        print(f"Unique players: {final_df['PLAYER_ID'].nunique()}")
        print(f"Seasons covered: {sorted(final_df['SEASON'].unique())}")
        date_min = final_df["GAME_DATE"].min()
        date_max = final_df["GAME_DATE"].max()
        print(f"Date range: {date_min} to {date_max}")

        # Save final results
        final_df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")

        # Display sample statistics
        display_summary_stats(final_df)

        return final_df
    else:
        print("No data was collected.")
        return pd.DataFrame()


def display_summary_stats(df: pd.DataFrame) -> None:
    """Display summary statistics of the collected data."""
    print("\n=== SUMMARY STATISTICS ===")

    # Overall stats
    print(f"Total games: {len(df):,}")
    print(f"Unique players: {df['PLAYER_ID'].nunique():,}")

    # Games by season
    games_by_season = df["SEASON"].value_counts().sort_index()
    print("\nGames by season:")
    for season, count in games_by_season.items():
        print(f"  {season}: {count:,} games")

    # Top scorers
    if "PTS" in df.columns:
        cols = ["GAME_DATE", "PLAYER_ID", "PTS", "SEASON"]
        top_games = df.nlargest(10, "PTS")[cols]
        print("\nTop 10 scoring games:")
        for _, game in top_games.iterrows():
            pts = game["PTS"]
            player_id = game["PLAYER_ID"]
            season = game["SEASON"]
            print(f"  Player {player_id}: {pts} pts ({season})")


def main():
    """Main execution function."""
    print("NBA Comprehensive Data Collection Script")
    print("=" * 50)

    # Configuration
    START_YEAR = 2010
    INCLUDE_PLAYOFFS = True
    BATCH_SIZE = 25  # Smaller batches for stability

    # Ask for user confirmation
    print(f"This will collect data from {START_YEAR} to present day.")
    print("This may take several hours and make thousands of API calls.")

    response = input("Do you want to proceed? (y/n): ").lower().strip()

    if response == "y":
        print("\nStarting data collection...")

        # Run collection
        all_data = collect_all_nba_data(
            start_year=START_YEAR,
            include_playoffs=INCLUDE_PLAYOFFS,
            batch_size=BATCH_SIZE,
            save_progress=True,
            output_file="nba_comprehensive_data_2010_to_present.csv",
        )

        if not all_data.empty:
            games_count = f"{len(all_data):,}"
            print(f"\nCollection successful! {games_count} games collected.")
            print("Data is ready for analysis and modeling.")
        else:
            print("\nCollection failed or no data collected.")
    else:
        print("Collection cancelled.")

        # Run a small demo instead
        print("\nRunning quick demo with limited data...")
        demo_data = collect_demo_data()

        if not demo_data.empty:
            print(f"Demo collected {len(demo_data)} games.")


def collect_demo_data() -> pd.DataFrame:
    """Collect a small sample of data for demonstration."""
    collector = DataCollector()

    # Get a few active players
    active_players = collector.get_active_players()
    if active_players.empty:
        return pd.DataFrame()

    # Take first 5 players
    demo_player_ids = active_players["PERSON_ID"].head(5).tolist()

    # Get data for just recent seasons
    demo_data = collector.collect_multiple_players(
        demo_player_ids, seasons=["2023-24"], include_playoffs=False
    )

    return demo_data


if __name__ == "__main__":
    main()
