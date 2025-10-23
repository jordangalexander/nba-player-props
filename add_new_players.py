#!/usr/bin/env python3
"""
Collect data for the 15 new recommended players and append to existing season files.

This script adds the 15 new players to our existing dataset without affecting
the original 30 players' data.
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


def get_new_15_players():
    """Get the 15 new recommended players to add to our dataset"""

    return [
        # Next 15 recommended players (data-driven selection)
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
    ]


def collect_new_players_for_season(season: str, collector: DataCollector):
    """Collect data for new players for a single season and append to existing file"""

    new_players = get_new_15_players()

    print(f"\n🏀 Adding {len(new_players)} new players to {season} data...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_data = []
    successful_players = []
    failed_players = []

    for i, player_name in enumerate(new_players, 1):
        print(f"\n📍 {i}/{len(new_players)}: {player_name}")

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
            if i < len(new_players):
                print("   ⏳ Waiting 4 seconds...")
                time.sleep(4)

        except Exception as e:
            failed_players.append(player_name)
            print(f"   ❌ Error: {str(e)}")
            print("   ⏳ Waiting 8 seconds before continuing...")
            time.sleep(8)

    # Combine new player data
    if all_data:
        new_combined_df = pd.concat(all_data, ignore_index=True)

        # Remove duplicates within new data
        initial_count = len(new_combined_df)
        new_combined_df = new_combined_df.drop_duplicates(
            subset=["PLAYER_ID", "Game_ID"]
        )
        new_final_count = len(new_combined_df)

        if initial_count != new_final_count:
            duplicates_removed = initial_count - new_final_count
            print(f"\n🔧 Removed {duplicates_removed} duplicate games in new data")

        # Check if season file already exists and append new players
        os.makedirs("data/player_box_scores", exist_ok=True)
        output_file = f"data/player_box_scores/nba_player_games_{season}.csv"

        if os.path.exists(output_file):
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

            print(
                f"📈 Added {new_games_added} games from {new_players_added} new players"
            )
            print(f"📊 Total: {original_games} → {len(combined_df)} games")
            print(f"👥 Players: {original_players} → {final_players} unique players")

        else:
            print(f"📄 Creating new file for {season} (no existing data)...")
            combined_df = new_combined_df

        # Save the combined file
        combined_df.to_csv(output_file, index=False)
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        print(f"\n🎉 {season} NEW PLAYERS ADDED!")
        print(f"   📊 Total games in file: {len(combined_df):,}")
        print(f"   👥 Total unique players: {combined_df['PLAYER_ID'].nunique()}")
        print(f"   ✅ New successful players: {len(successful_players)}")
        print(f"   ❌ New failed players: {len(failed_players)}")
        print(f"   💾 File: {output_file} ({file_size_mb:.1f} MB)")

        if combined_df["GAME_DATE"].notna().any():
            date_range = (
                f"{combined_df['GAME_DATE'].min()} to {combined_df['GAME_DATE'].max()}"
            )
            print(f"   📅 Date range: {date_range}")

        return combined_df, successful_players, failed_players
    else:
        print(f"\n❌ No new data collected for {season}")
        return pd.DataFrame(), [], new_players


def main():
    """Main function for adding new players to existing data"""

    parser = argparse.ArgumentParser(
        description="Add 15 new players to existing NBA dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_new_players.py --seasons 2023-24 2024-25
  python add_new_players.py --seasons 2022-23
  python add_new_players.py --start 2020 --end 2024
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--seasons", nargs="+", help="Specific seasons (e.g., 2023-24 2024-25)"
    )
    group.add_argument("--start", type=int, help="Start year for range")

    parser.add_argument(
        "--end", type=int, help="End year for range (required with --start)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay between API calls (default: 3.0 for conservative approach)",
    )

    args = parser.parse_args()

    # Parse seasons
    seasons = []
    if args.seasons:
        for season in args.seasons:
            if "-" in season and len(season) == 7:  # Format: 2023-24
                seasons.append(season)
            elif len(season) == 4 and season.isdigit():  # Format: 2023
                year = int(season)
                seasons.append(f"{year}-{str(year + 1)[2:]}")
            else:
                print(f"⚠️ Unknown season format: {season}")
    elif args.start:
        if not args.end:
            parser.error("--end is required when using --start")
        for year in range(args.start, args.end + 1):
            seasons.append(f"{year}-{str(year + 1)[2:]}")

    if not seasons:
        print("❌ No valid seasons specified")
        return

    print("🔄 ADDING NEW PLAYERS TO EXISTING NBA DATASET")
    print(f"👥 Adding: {len(get_new_15_players())} new players")
    print(f"📋 Seasons: {seasons}")
    print(f"⏱️ API delay: {args.delay}s between calls")
    print("📁 Appending to: data/player_box_scores/")
    print("=" * 60)

    start_time = datetime.now()
    collector = DataCollector(rate_limit_delay=args.delay)

    all_successful = True
    collection_summary = {}

    # Add new players to each season
    for season in seasons:
        try:
            season_df, successful, failed = collect_new_players_for_season(
                season, collector
            )
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

    end_time = datetime.now()

    # Final summary
    print("\n🏁 NEW PLAYERS ADDITION COMPLETE!")
    print(f"⏱️ Total time: {end_time - start_time}")
    print(f"📊 Status: {'✅ All successful' if all_successful else '⚠️ Some issues'}")

    print("\n📈 ADDITION SUMMARY:")
    total_new_games = 0
    for season, stats in collection_summary.items():
        status = "✅" if stats["failed"] == 0 else "⚠️"
        success_rate = f"{stats['successful']}/{stats['successful'] + stats['failed']}"
        print(f"   {status} {season}: {stats['games']:,} games, {success_rate} players")
        total_new_games += stats["games"]

    print(f"\n🎯 TOTAL NEW GAMES ADDED: {total_new_games:,}")

    # Show updated file structure
    print("\n📂 UPDATED FILES:")
    data_dir = "data/player_box_scores"
    if os.path.exists(data_dir):
        files = [
            f
            for f in os.listdir(data_dir)
            if f.endswith(".csv") and "nba_player_games_" in f
        ]
        for file in sorted(files):
            file_path = os.path.join(data_dir, file)
            try:
                df = pd.read_csv(file_path)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                players = df["PLAYER_ID"].nunique()
                games = len(df)
                print(
                    f"   📄 {file}: {games:,} games, {players} players ({size_mb:.1f} MB)"
                )
            except Exception as e:
                print(f"   ❌ Error reading {file}: {e}")

    print(
        "\n🎉 Dataset expanded! Now ready to regenerate master dataset with all 45 players."
    )


if __name__ == "__main__":
    main()
