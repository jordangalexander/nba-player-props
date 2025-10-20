#!/usr/bin/env python3
"""
Parameterized NBA data collection for any season range
Usage: python collect_nba_data.py --seasons 2022-23 2023-24 2024-25
       python collect_nba_data.py --seasons 2022-23  # Single season
       python collect_nba_data.py --start 2020 --end 2024  # Range
"""

import argparse
import os
import time
from datetime import datetime

import pandas as pd

from nba_player_props.data_collector.data_collector import DataCollector


def get_target_players():
    """Get the same 30 key players for all collections"""

    return [
        # Core superstars
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
        # All-stars and key players
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
        # Rising stars and key role players
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
    ]


def collect_season_data(season: str, collector: DataCollector):
    """Collect data for a single season"""

    target_players = get_target_players()

    print(f"\n🏀 Collecting {season} data for {len(target_players)} players...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_data = []
    successful_players = []
    failed_players = []

    for i, player_name in enumerate(target_players, 1):
        print(f"\n📍 {i}/{len(target_players)}: {player_name}")

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
            if i < len(target_players):
                print("   ⏳ Waiting 4 seconds...")
                time.sleep(4)

        except Exception as e:
            failed_players.append(player_name)
            print(f"   ❌ Error: {str(e)}")
            print("   ⏳ Waiting 8 seconds before continuing...")
            time.sleep(8)

    # Combine and save season data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Remove duplicates
        initial_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=["PLAYER_ID", "Game_ID"])
        final_count = len(combined_df)

        if initial_count != final_count:
            print(f"\n🔧 Removed {initial_count - final_count} duplicate games")

        # Save individual season file
        os.makedirs("data/player_box_scores", exist_ok=True)
        output_file = f"data/player_box_scores/nba_player_games_{season}.csv"
        combined_df.to_csv(output_file, index=False)

        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        print(f"\n🎉 {season} COLLECTION SUCCESS!")
        print(f"   📊 Total games collected: {len(combined_df):,}")
        print(f"   👥 Unique players: {combined_df['PLAYER_ID'].nunique()}")
        print(f"   ✅ Successful players: {len(successful_players)}")
        print(f"   ❌ Failed players: {len(failed_players)}")
        print(f"   💾 Saved to: {output_file} ({file_size_mb:.1f} MB)")

        if combined_df["GAME_DATE"].notna().any():
            date_range = (
                f"{combined_df['GAME_DATE'].min()} to {combined_df['GAME_DATE'].max()}"
            )
            print(f"   📅 Date range: {date_range}")

        return combined_df, successful_players, failed_players
    else:
        print(f"\n❌ No data collected for {season}")
        return pd.DataFrame(), [], target_players


def create_combined_dataset(seasons: list):
    """Create combined dataset from all collected seasons"""

    print(f"\n📁 Creating combined dataset from {len(seasons)} seasons...")

    # Find all season files
    data_dir = "data/player_box_scores"
    season_files = []

    for season in seasons:
        file_path = f"{data_dir}/nba_player_games_{season}.csv"
        if os.path.exists(file_path):
            season_files.append((season, file_path))
        else:
            print(f"   ⚠️ Missing file for {season}: {file_path}")

    if not season_files:
        print("❌ No season files found")
        return None

    print(f"📊 Found {len(season_files)} season files:")

    all_data = []
    season_summary = {}

    for season, file_path in season_files:
        try:
            df = pd.read_csv(file_path)
            all_data.append(df)

            season_summary[season] = {
                "games": len(df),
                "players": df["PLAYER_ID"].nunique(),
            }

            print(
                f"   ✅ {season}: {len(df):,} games, {df['PLAYER_ID'].nunique()} players"
            )

        except Exception as e:
            print(f"   ❌ Error loading {season}: {str(e)}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Remove duplicates across seasons
        initial_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=["PLAYER_ID", "Game_ID"])
        final_count = len(combined_df)

        if initial_count != final_count:
            print(
                f"🔧 Removed {initial_count - final_count} duplicate games across seasons"
            )

        # Save combined dataset
        seasons_str = "_".join(seasons)
        output_file = f"data/player_box_scores/nba_combined_{seasons_str}.csv"
        combined_df.to_csv(output_file, index=False)

        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        print("\n🎯 COMBINED DATASET CREATED:")
        print(f"   📊 Total games: {len(combined_df):,}")
        print(f"   👥 Unique players: {combined_df['PLAYER_ID'].nunique()}")

        if "PLAYER_NAME" in combined_df.columns:
            print(f"   🏷️ Player names: {combined_df['PLAYER_NAME'].nunique()} unique")

        if (
            "GAME_DATE" in combined_df.columns
            and combined_df["GAME_DATE"].notna().any()
        ):
            date_range = (
                f"{combined_df['GAME_DATE'].min()} to {combined_df['GAME_DATE'].max()}"
            )
            print(f"   📅 Date range: {date_range}")

        if "SEASON" in combined_df.columns:
            seasons_covered = sorted(combined_df["SEASON"].unique())
            print(f"   🏀 Seasons: {seasons_covered}")

        print(f"   💾 File: {output_file} ({file_size_mb:.1f} MB)")

        # Season breakdown
        print("\n📈 SEASON BREAKDOWN:")
        for season, stats in sorted(season_summary.items()):
            print(
                f"   🏀 {season}: {stats['games']:,} games, {stats['players']} players"
            )

        # Statistics
        if "PTS" in combined_df.columns:
            print("\n📊 OVERALL STATISTICS:")
            print(f"   🏀 Average points: {combined_df['PTS'].mean():.1f}")

            if "SEASON" in combined_df.columns:
                season_avg = combined_df.groupby("SEASON")["PTS"].mean()
                for season, avg in season_avg.items():
                    print(f"   📈 {season} avg points: {avg:.1f}")

        if "REB" in combined_df.columns:
            print(f"   🏀 Average rebounds: {combined_df['REB'].mean():.1f}")

        if "AST" in combined_df.columns:
            print(f"   🏀 Average assists: {combined_df['AST'].mean():.1f}")

        return combined_df

    return None


def parse_seasons(seasons_input):
    """Parse season input into list of season strings"""

    if not seasons_input:
        return []

    seasons = []
    for season in seasons_input:
        # Handle different formats
        if "-" in season and len(season) == 7:  # Format: 2023-24
            seasons.append(season)
        elif len(season) == 4 and season.isdigit():  # Format: 2023
            year = int(season)
            seasons.append(f"{year}-{str(year + 1)[2:]}")
        else:
            print(f"⚠️ Unknown season format: {season}")

    return seasons


def generate_season_range(start_year: int, end_year: int):
    """Generate list of seasons from start to end year"""

    seasons = []
    for year in range(start_year, end_year + 1):
        seasons.append(f"{year}-{str(year + 1)[2:]}")

    return seasons


def main():
    """Main function with argument parsing"""

    parser = argparse.ArgumentParser(
        description="Collect NBA player box score data for specified seasons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python collect_nba_data.py --seasons 2022-23 2023-24 2024-25
  python collect_nba_data.py --seasons 2023-24
  python collect_nba_data.py --start 2020 --end 2024
  python collect_nba_data.py --seasons 2022 2023 2024  # Also works
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--seasons", nargs="+", help="Specific seasons (e.g., 2023-24 2024-25)"
    )
    group.add_argument("--start", type=int, help="Start year for range (e.g., 2020)")

    parser.add_argument(
        "--end", type=int, help="End year for range (required with --start)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between API calls (default: 2.0)",
    )
    parser.add_argument(
        "--no-combine", action="store_true", help="Skip creating combined dataset"
    )

    args = parser.parse_args()

    # Determine seasons to collect
    if args.seasons:
        seasons = parse_seasons(args.seasons)
    elif args.start:
        if not args.end:
            parser.error("--end is required when using --start")
        seasons = generate_season_range(args.start, args.end)
    else:
        parser.error("Must specify either --seasons or --start/--end")

    if not seasons:
        print("❌ No valid seasons specified")
        return

    print("🏀 PARAMETERIZED NBA DATA COLLECTION")
    print(f"📋 Seasons to collect: {seasons}")
    print(f"👥 Players: {len(get_target_players())} key players")
    print("📁 Output: data/player_box_scores/")
    print(f"⏱️ API delay: {args.delay}s between calls")
    print("=" * 60)

    start_time = datetime.now()
    collector = DataCollector(rate_limit_delay=args.delay)

    all_successful = True
    collection_summary = {}

    # Collect data for each season
    for season in seasons:
        try:
            season_df, successful, failed = collect_season_data(season, collector)
            collection_summary[season] = {
                "games": len(season_df) if not season_df.empty else 0,
                "successful": len(successful),
                "failed": len(failed),
            }

            if season_df.empty or failed:
                all_successful = False

            # Pause between seasons
            if season != seasons[-1]:
                print("\n⏳ Waiting 10 seconds before next season...")
                time.sleep(10)

        except Exception as e:
            print(f"\n❌ Critical error for {season}: {str(e)}")
            all_successful = False

    # Create combined dataset unless skipped
    combined_df = None
    if not args.no_combine:
        combined_df = create_combined_dataset(seasons)

    end_time = datetime.now()

    # Final summary
    print("\n🏁 COLLECTION COMPLETE!")
    print(f"⏱️ Total time: {end_time - start_time}")
    print(f"📊 Status: {'✅ All successful' if all_successful else '⚠️ Some issues'}")

    print("\n📈 COLLECTION SUMMARY:")
    total_games = 0
    for season, stats in collection_summary.items():
        status = "✅" if stats["failed"] == 0 else "⚠️"
        print(
            f"   {status} {season}: {stats['games']:,} games, {stats['successful']}/{stats['successful'] + stats['failed']} players"
        )
        total_games += stats["games"]

    print(f"\n🎯 TOTAL: {total_games:,} games collected")

    if combined_df is not None:
        print(f"🎉 Combined dataset: {len(combined_df):,} games ready for analysis!")

    # Show file structure
    print("\n📂 FILES CREATED:")
    data_dir = "data/player_box_scores"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        for file in sorted(files):
            file_path = os.path.join(data_dir, file)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            file_type = "[COMBINED]" if "combined" in file else "[INDIVIDUAL]"
            print(f"   📄 {file} ({size_mb:.1f} MB) {file_type}")


if __name__ == "__main__":
    main()
