#!/usr/bin/env python3
"""
Flexible NBA Data Collection Script

This script allows you to collect NBA data for any list of players across any date range.
Much more modular and reusable than the previous approach.
"""

import argparse
import os
import sys
import time
from datetime import datetime

import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from nba_player_props.data_collector.data_collector import DataCollector


def collect_players_for_seasons(
    player_names: list[str],
    seasons: list[str],
    delay: float = 3.0,
    append_to_existing: bool = True,
    output_dir: str = "data/player_box_scores",
) -> dict:
    """
    Collect NBA data for specified players across specified seasons.

    Args:
        player_names: List of player names to collect data for
        seasons: List of seasons in format ["2023-24", "2022-23", ...]
        delay: Seconds to wait between API calls (default: 3.0)
        append_to_existing: Whether to append to existing files or overwrite
        output_dir: Directory to save data files

    Returns:
        Dictionary with collection results per season
    """

    print("🔄 FLEXIBLE NBA DATA COLLECTION")
    print(f"👥 Players: {len(player_names)} players")
    print(f"📋 Seasons: {seasons}")
    print(f"⏱️ API delay: {delay}s between calls")
    print(f"📁 Output: {output_dir}/")
    print(f"📄 Mode: {'Append' if append_to_existing else 'Overwrite'}")
    print("=" * 60)

    collector = DataCollector(rate_limit_delay=delay)
    collection_summary = {}

    for season_idx, season in enumerate(seasons, 1):
        print(f"\n🏀 Processing season {season} ({season_idx}/{len(seasons)})...")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        season_results = collect_players_for_single_season(
            player_names=player_names,
            season=season,
            collector=collector,
            append_to_existing=append_to_existing,
            output_dir=output_dir,
        )

        collection_summary[season] = season_results

        # Pause between seasons
        if season_idx < len(seasons):
            print("\n⏳ Waiting 10 seconds before next season...")
            time.sleep(10)

    return collection_summary


def collect_players_for_single_season(
    player_names: list[str],
    season: str,
    collector: DataCollector,
    append_to_existing: bool = True,
    output_dir: str = "data/player_box_scores",
) -> dict:
    """
    Collect data for all specified players in a single season.

    Returns:
        Dictionary with collection results for this season
    """

    all_data = []
    successful_players = []
    failed_players = []

    for i, player_name in enumerate(player_names, 1):
        print(f"\n📍 {i}/{len(player_names)}: {player_name}")

        try:
            player_data = collector.get_player_data_by_name(
                player_name=player_name, seasons=[season], include_playoffs=True
            )

            if not player_data.empty:
                all_data.append(player_data)
                successful_players.append(player_name)
                print(f"   ✅ Collected {len(player_data)} games")
            else:
                failed_players.append(player_name)
                print("   ⚠️ No data found")

            # Conservative delay between players
            if i < len(player_names):
                print("   ⏳ Waiting 4 seconds...")
                time.sleep(4)

        except Exception as e:
            failed_players.append(player_name)
            print(f"   ❌ Error: {str(e)}")
            print("   ⏳ Waiting 8 seconds before continuing...")
            time.sleep(8)

    # Process and save the collected data
    if all_data:
        return save_season_data(
            all_data=all_data,
            season=season,
            successful_players=successful_players,
            failed_players=failed_players,
            append_to_existing=append_to_existing,
            output_dir=output_dir,
        )
    else:
        print(f"\n❌ No data collected for {season}")
        return {
            "games": 0,
            "successful": 0,
            "failed": len(player_names),
            "file_created": False,
        }


def save_season_data(
    all_data: list[pd.DataFrame],
    season: str,
    successful_players: list[str],
    failed_players: list[str],
    append_to_existing: bool,
    output_dir: str,
) -> dict:
    """
    Save collected data to appropriate file, handling append vs overwrite logic.
    """

    # Combine new player data
    new_combined_df = pd.concat(all_data, ignore_index=True)

    # Remove duplicates within new data
    initial_count = len(new_combined_df)
    new_combined_df = new_combined_df.drop_duplicates(subset=["PLAYER_ID", "Game_ID"])
    new_final_count = len(new_combined_df)

    if initial_count != new_final_count:
        duplicates_removed = initial_count - new_final_count
        print(f"\n🔧 Removed {duplicates_removed} duplicate games in new data")

    # Prepare output file
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/nba_player_games_{season}.csv"

    if append_to_existing and os.path.exists(output_file):
        print(f"📄 Found existing {season} file, appending new players...")
        existing_df = pd.read_csv(output_file)
        original_games = len(existing_df)
        original_players = existing_df["PLAYER_ID"].nunique()

        # Combine existing and new data
        combined_df = pd.concat([existing_df, new_combined_df], ignore_index=True)

        # Remove duplicates across all data
        pre_dedup_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=["PLAYER_ID", "Game_ID"])
        post_dedup_count = len(combined_df)

        if pre_dedup_count != post_dedup_count:
            cross_duplicates = pre_dedup_count - post_dedup_count
            print(f"🔧 Removed {cross_duplicates} cross-duplicates after merging")

        new_games_added = len(combined_df) - original_games
        final_players = combined_df["PLAYER_ID"].nunique()
        new_players_added = final_players - original_players

        print(f"📈 Added {new_games_added} games from {new_players_added} new players")
        print(f"📊 Total: {original_games} → {len(combined_df)} games")
        print(f"👥 Players: {original_players} → {final_players} unique players")

    else:
        if append_to_existing:
            print(f"📄 Creating new file for {season} (no existing data)...")
        else:
            print(f"📄 Overwriting file for {season}...")
        combined_df = new_combined_df

    # Save the file
    combined_df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print(f"\n🎉 {season} COLLECTION SUCCESS!")
    print(f"   📊 Total games in file: {len(combined_df):,}")
    print(f"   👥 Total unique players: {combined_df['PLAYER_ID'].nunique()}")
    print(f"   ✅ New successful players: {len(successful_players)}")
    print(f"   ❌ New failed players: {len(failed_players)}")
    print(f"   💾 File: {output_file} ({file_size_mb:.1f} MB)")

    if combined_df["GAME_DATE"].notna().any():
        # Ensure GAME_DATE is datetime for proper min/max calculation
        combined_df["GAME_DATE"] = pd.to_datetime(
            combined_df["GAME_DATE"], errors="coerce", format="mixed"
        )
        min_date = combined_df["GAME_DATE"].min().strftime("%Y-%m-%d")
        max_date = combined_df["GAME_DATE"].max().strftime("%Y-%m-%d")
        date_range = f"{min_date} to {max_date}"
        print(f"   📅 Date range: {date_range}")

    return {
        "games": len(combined_df),
        "successful": len(successful_players),
        "failed": len(failed_players),
        "file_created": True,
        "file_path": output_file,
        "file_size_mb": file_size_mb,
    }


def get_predefined_player_lists():
    """Get predefined lists of players for common use cases"""

    return {
        "legends_2000s": [
            "LeBron James",
            "Kobe Bryant",
            "Tim Duncan",
            "Shaquille O'Neal",
            "Steve Nash",
            "Dirk Nowitzki",
            "Kevin Garnett",
            "Paul Pierce",
            "Allen Iverson",
            "Tracy McGrady",
            "Vince Carter",
            "Ray Allen",
            "Chauncey Billups",
            "Rasheed Wallace",
            "Ben Wallace",
            "Chris Webber",
            "Carmelo Anthony",
            "Chris Paul",
            "Dwyane Wade",
            "Dwight Howard",
        ],
        "third_wave_15": [
            "Fred VanVleet",
            "Nikola Vucevic",
            "Kristaps Porzingis",
            "Jalen Williams",
            "Tobias Harris",
            "Cam Thomas",
            "Immanuel Quickley",
            "Myles Turner",
            "Clint Capela",
            "Terry Rozier",
            "Jerami Grant",
            "Nic Claxton",
            "Jonas Valanciunas",
            "Keyonte George",
            "Trey Murphy III",
        ],
        "second_wave_15": [
            "Domantas Sabonis",
            "Jalen Brunson",
            "Pascal Siakam",
            "Donovan Mitchell",
            "Julius Randle",
            "Bam Adebayo",
            "Jaylen Brown",
            "Karl-Anthony Towns",
            "Brandon Ingram",
            "Coby White",
            "Anfernee Simons",
            "Jaren Jackson Jr.",
            "Darius Garland",
            "Derrick White",
            "CJ McCollum",
        ],
        "original_30": [
            "LeBron James",
            "Stephen Curry",
            "Kevin Durant",
            "Giannis Antetokounmpo",
            "Luka Doncic",
            "Jayson Tatum",
            "Joel Embiid",
            "Nikola Jokic",
            "Damian Lillard",
            "Anthony Davis",
            "Kawhi Leonard",
            "Jimmy Butler",
            "Ja Morant",
            "Devin Booker",
            "Zion Williamson",
            "Anthony Edwards",
            "Paolo Banchero",
            "Victor Wembanyama",
            "Scottie Barnes",
            "Franz Wagner",
            "Tyrese Haliburton",
            "De'Aaron Fox",
            "Tyler Herro",
            "Lauri Markkanen",
            "Alperen Sengun",
            "Cade Cunningham",
            "Evan Mobley",
            "Jalen Green",
            "Desmond Bane",
            "Mikal Bridges",
        ],
    }


def parse_season_range(start_year: int, end_year: int) -> list[str]:
    """Generate list of seasons from start to end year"""
    seasons = []
    for year in range(start_year, end_year + 1):
        seasons.append(f"{year}-{str(year + 1)[2:]}")
    return seasons


def parse_seasons_input(seasons_input: list[str]) -> list[str]:
    """Parse season input into standardized format"""
    seasons = []
    for season in seasons_input:
        if "-" in season and len(season) == 7:  # Format: 2023-24
            seasons.append(season)
        elif len(season) == 4 and season.isdigit():  # Format: 2023
            year = int(season)
            seasons.append(f"{year}-{str(year + 1)[2:]}")
        else:
            print(f"⚠️ Unknown season format: {season}")
    return seasons


def main():
    """Main function with flexible argument parsing"""

    parser = argparse.ArgumentParser(
        description="Flexible NBA data collection for any players and seasons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect third wave players for recent seasons
  python flexible_collect.py --players third_wave_15 --seasons 2023-24 2024-25
  
  # Collect custom players for a range of years
  python flexible_collect.py --players "LeBron James,Stephen Curry" --start 2020 --end 2024
  
  # Collect predefined list for specific seasons
  python flexible_collect.py --players second_wave_15 --seasons 2018-19 2019-20
        """,
    )

    # Player selection
    player_group = parser.add_mutually_exclusive_group(required=True)
    player_group.add_argument(
        "--players",
        help="Comma-separated player names OR predefined list (legends_2000s, third_wave_15, second_wave_15, original_30)",
    )
    player_group.add_argument(
        "--player-list",
        help="Use predefined player list: legends_2000s, third_wave_15, second_wave_15, original_30",
    )

    # Season selection
    season_group = parser.add_mutually_exclusive_group(required=True)
    season_group.add_argument(
        "--seasons", nargs="+", help="Specific seasons (e.g., 2023-24 2024-25)"
    )
    season_group.add_argument("--start", type=int, help="Start year for range")

    parser.add_argument(
        "--end", type=int, help="End year for range (required with --start)"
    )
    parser.add_argument(
        "--delay", type=float, default=3.0, help="Delay between API calls"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite instead of append"
    )
    parser.add_argument(
        "--output-dir", default="data/player_box_scores", help="Output directory"
    )

    args = parser.parse_args()

    # Parse players
    predefined_lists = get_predefined_player_lists()

    if args.player_list:
        if args.player_list in predefined_lists:
            player_names = predefined_lists[args.player_list]
        else:
            print(f"❌ Unknown player list: {args.player_list}")
            print(f"Available lists: {list(predefined_lists.keys())}")
            return
    elif args.players:
        if args.players in predefined_lists:
            player_names = predefined_lists[args.players]
        else:
            # Parse comma-separated list
            player_names = [name.strip() for name in args.players.split(",")]
    else:
        print("❌ Must specify players")
        return

    # Parse seasons
    if args.seasons:
        seasons = parse_seasons_input(args.seasons)
    elif args.start:
        if not args.end:
            parser.error("--end is required when using --start")
        seasons = parse_season_range(args.start, args.end)
    else:
        print("❌ Must specify seasons")
        return

    if not seasons:
        print("❌ No valid seasons specified")
        return

    print(
        f"🎯 Collecting data for {len(player_names)} players across {len(seasons)} seasons"
    )

    # Run the collection
    start_time = datetime.now()

    collection_summary = collect_players_for_seasons(
        player_names=player_names,
        seasons=seasons,
        delay=args.delay,
        append_to_existing=not args.overwrite,
        output_dir=args.output_dir,
    )

    end_time = datetime.now()

    # Final summary
    print("\n🏁 COLLECTION COMPLETE!")
    print(f"⏱️ Total time: {end_time - start_time}")

    total_games = 0
    total_successful = 0
    total_failed = 0

    print("\n📈 FINAL SUMMARY:")
    for season, results in collection_summary.items():
        status = "✅" if results["failed"] == 0 else "⚠️"
        print(
            f"   {status} {season}: {results['games']:,} games, "
            + f"{results['successful']}/{results['successful'] + results['failed']} players"
        )
        total_games += results["games"]
        total_successful += results["successful"]
        total_failed += results["failed"]

    print(
        f"\n🎯 TOTALS: {total_games:,} games, {total_successful} successful, {total_failed} failed"
    )
    print(f"🚀 Ready for analysis with expanded {len(player_names)} player dataset!")


if __name__ == "__main__":
    main()
