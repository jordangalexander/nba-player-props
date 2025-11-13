#!/usr/bin/env python3
"""
Smart NBA Data Updater

Auto-detects current season, checks existing data, and updates through today.
Leverages flexible_collect.py logic for targeted data collection.

Usage:
    python update_data.py                           # Update all tracked players for current season
    python update_data.py --players original_30     # Update specific player list
    python update_data.py --season 2024-25          # Update specific season
    python update_data.py --check                   # Check what data you have
"""

import argparse
import os
import sys
from datetime import datetime

import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nba_player_props.data_collector.data_collector import DataCollector


def get_current_season() -> str:
    """Auto-detect current NBA season based on today's date.

    NBA seasons start in October. So:
    - Jan-Sep: Previous year's season (e.g., Nov 2025 -> 2025-26)
    - Oct-Dec: Current year's season starts
    """
    now = datetime.now()
    year = now.year
    month = now.month

    # If we're in Oct-Dec, the season started this year
    # If we're in Jan-Sep, we're in the season that started last year
    if month >= 10:  # October or later
        season_start = year
    else:
        season_start = year - 1

    return f"{season_start}-{str(season_start + 1)[2:]}"


def check_existing_data(data_dir: str = "data/player_box_scores") -> dict:
    """Check what data files exist and their stats.

    Returns:
        Dictionary with season info
    """
    if not os.path.exists(data_dir):
        return {}

    season_files = [
        f
        for f in os.listdir(data_dir)
        if f.startswith("nba_player_games_") and f.endswith(".csv")
    ]

    season_info = {}

    for file in sorted(season_files):
        season = file.replace("nba_player_games_", "").replace(".csv", "")
        file_path = os.path.join(data_dir, file)

        try:
            df = pd.read_csv(file_path)
            df["GAME_DATE"] = pd.to_datetime(
                df["GAME_DATE"], format="mixed", errors="coerce"
            )

            season_info[season] = {
                "file": file,
                "games": len(df),
                "players": df["Player_ID"].nunique()
                if "Player_ID" in df.columns
                else 0,
                "date_range": f"{df['GAME_DATE'].min().strftime('%Y-%m-%d')} to {df['GAME_DATE'].max().strftime('%Y-%m-%d')}"
                if not df["GAME_DATE"].isna().all()
                else "Unknown",
                "last_updated": datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as e:
            season_info[season] = {"file": file, "error": str(e)}

    return season_info


def display_data_status():
    """Display current data status."""
    print("📊 NBA DATA STATUS REPORT")
    print("=" * 70)
    print(f"📅 Today: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🏀 Current Season: {get_current_season()}")
    print()

    season_info = check_existing_data()

    if not season_info:
        print("❌ No data files found in data/player_box_scores/")
        return

    print(f"📁 Found {len(season_info)} season files:\n")

    current_season = get_current_season()

    for season, info in season_info.items():
        if "error" in info:
            print(f"  ⚠️  {season}: Error - {info['error']}")
            continue

        status = "🟢 CURRENT" if season == current_season else "⚪ HISTORICAL"
        print(f"  {status} {season}")
        print(f"     Games: {info['games']:,} | Players: {info['players']}")
        print(f"     Date Range: {info['date_range']}")
        print(f"     Last Updated: {info['last_updated']}")
        print()

    # Check if current season exists
    if current_season not in season_info:
        print(f"⚠️  MISSING: No data for current season ({current_season})")
        print("   → Run: python update_data.py")
    else:
        # Check if current season is up to date
        current_info = season_info[current_season]
        if "date_range" in current_info:
            try:
                last_game = datetime.strptime(
                    current_info["date_range"].split(" to ")[1], "%Y-%m-%d"
                )
                days_old = (datetime.now() - last_game).days

                if days_old > 7:
                    print(f"⚠️  Data for {current_season} is {days_old} days old")
                    print("   → Run: python update_data.py")
                else:
                    print(f"✅ Current season data is up to date ({days_old} days old)")
            except:
                pass


def get_predefined_player_lists():
    """Get predefined lists of players (from flexible_collect.py)."""
    return {
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
    }


def collect_players_for_season(
    player_names: list[str],
    season: str,
    output_dir: str = "data/player_box_scores",
    delay: float = 2.0,
) -> dict:
    """Collect data for players in a season (adapted from flexible_collect.py)."""
    import time

    print(f"\n🏀 Collecting {season} data for {len(player_names)} players...")
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}\n")

    collector = DataCollector(rate_limit_delay=delay)

    all_data = []
    successful_players = []
    failed_players = []

    for i, player_name in enumerate(player_names, 1):
        print(f"📍 {i}/{len(player_names)}: {player_name}")

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
                print("   ⚠️  No data found")

            # Delay between players
            if i < len(player_names):
                time.sleep(delay)

        except Exception as e:
            failed_players.append(player_name)
            print(f"   ❌ Error: {str(e)}")
            time.sleep(delay * 2)  # Longer delay on error

    # Save the data
    if all_data:
        return save_season_data(
            all_data=all_data,
            season=season,
            successful_players=successful_players,
            failed_players=failed_players,
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
    output_dir: str,
) -> dict:
    """Save collected data with smart append/merge logic."""
    # Combine new data
    new_combined_df = pd.concat(all_data, ignore_index=True)

    # Remove duplicates within new data
    initial_count = len(new_combined_df)
    new_combined_df = new_combined_df.drop_duplicates(subset=["Player_ID", "Game_ID"])
    new_final_count = len(new_combined_df)

    if initial_count != new_final_count:
        print(
            f"\n🔧 Removed {initial_count - new_final_count} duplicate games in new data"
        )

    # Prepare output file
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/nba_player_games_{season}.csv"

    # Check for existing file and merge
    if os.path.exists(output_file):
        print(f"📄 Found existing {season} file, merging...")
        existing_df = pd.read_csv(output_file)
        original_games = len(existing_df)

        # Combine
        combined_df = pd.concat([existing_df, new_combined_df], ignore_index=True)

        # Remove cross-duplicates
        pre_dedup = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=["Player_ID", "Game_ID"])
        post_dedup = len(combined_df)

        if pre_dedup != post_dedup:
            print(f"🔧 Removed {pre_dedup - post_dedup} duplicates after merge")

        new_games = len(combined_df) - original_games
        print(
            f"📈 Added {new_games} new games (was {original_games:,}, now {len(combined_df):,})"
        )
    else:
        print(f"📄 Creating new file for {season}")
        combined_df = new_combined_df

    # Save
    combined_df.to_csv(output_file, index=False)
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print("\n🎉 SUCCESS!")
    print(f"   💾 File: {output_file}")
    print(f"   📊 Total games: {len(combined_df):,}")
    print(f"   👥 Unique players: {combined_df['Player_ID'].nunique()}")
    print(f"   ✅ Successfully collected: {len(successful_players)}")
    print(f"   ❌ Failed: {len(failed_players)}")
    print(f"   💿 Size: {file_size_mb:.2f} MB")

    # Show date range
    if "GAME_DATE" in combined_df.columns:
        combined_df["GAME_DATE"] = pd.to_datetime(
            combined_df["GAME_DATE"], format="mixed", errors="coerce"
        )
        if not combined_df["GAME_DATE"].isna().all():
            min_date = combined_df["GAME_DATE"].min().strftime("%Y-%m-%d")
            max_date = combined_df["GAME_DATE"].max().strftime("%Y-%m-%d")
            print(f"   📅 Date range: {min_date} to {max_date}")

    return {
        "games": len(combined_df),
        "successful": len(successful_players),
        "failed": len(failed_players),
        "file_created": True,
        "file_path": output_file,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smart NBA data updater - auto-detects and updates through today",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_data.py                      # Update all players for current season
  python update_data.py --check              # Check data status
  python update_data.py --players original_30  # Update specific list
  python update_data.py --season 2024-25     # Update specific season
  python update_data.py --all-players        # Update all tracked player lists
        """,
    )

    parser.add_argument(
        "--check", action="store_true", help="Check current data status and exit"
    )

    parser.add_argument(
        "--season",
        help="Specific season to update (e.g., 2025-26). Default: current season",
    )

    parser.add_argument(
        "--players",
        help="Player list: original_30, second_wave_15, third_wave_15, or 'all-tracked'",
    )

    parser.add_argument(
        "--all-players",
        action="store_true",
        help="Update all tracked players (original_30 + second_wave_15 + third_wave_15)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between API calls (default: 2.0 seconds)",
    )

    args = parser.parse_args()

    # Check mode
    if args.check:
        display_data_status()
        return

    # Determine season
    season = args.season if args.season else get_current_season()

    # Determine players
    player_lists = get_predefined_player_lists()

    if args.all_players:
        # Combine all lists
        all_players = (
            player_lists["original_30"]
            + player_lists["second_wave_15"]
            + player_lists["third_wave_15"]
        )
        print(f"🎯 Updating ALL tracked players ({len(all_players)} total)")
    elif args.players:
        if args.players == "all-tracked":
            all_players = (
                player_lists["original_30"]
                + player_lists["second_wave_15"]
                + player_lists["third_wave_15"]
            )
        elif args.players in player_lists:
            all_players = player_lists[args.players]
            print(f"🎯 Updating '{args.players}' list ({len(all_players)} players)")
        else:
            print(f"❌ Unknown player list: {args.players}")
            print(f"Available: {', '.join(player_lists.keys())}, all-tracked")
            return
    else:
        # Default: use all tracked players
        all_players = (
            player_lists["original_30"]
            + player_lists["second_wave_15"]
            + player_lists["third_wave_15"]
        )
        print(
            f"🎯 Updating all tracked players ({len(all_players)} total) for {season}"
        )

    print(f"📅 Season: {season}")
    print(f"⏱️  API Delay: {args.delay}s")
    print("=" * 70)

    # Collect data
    start_time = datetime.now()
    results = collect_players_for_season(
        player_names=all_players, season=season, delay=args.delay
    )
    end_time = datetime.now()

    # Summary
    print("\n" + "=" * 70)
    print("🏁 UPDATE COMPLETE!")
    print(f"⏱️  Duration: {end_time - start_time}")
    print(f"📊 Games collected: {results['games']:,}")
    print(
        f"✅ Successful: {results['successful']}/{results['successful'] + results['failed']}"
    )

    if results["file_created"]:
        print(f"\n💾 Data saved to: {results['file_path']}")
        print("🚀 Ready for analysis!")


if __name__ == "__main__":
    main()
