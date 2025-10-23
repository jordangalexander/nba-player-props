#!/usr/bin/env python3
"""
Batch backfill script for the 15 new players across all historical seasons
"""

import os
import subprocess
import sys
import time


def get_missing_seasons():
    """Get list of seasons that need the 15 new players added"""

    # All seasons we have historical data for
    all_seasons = [
        "2010-11",
        "2011-12",
        "2012-13",
        "2013-14",
        "2014-15",
        "2015-16",
        "2016-17",
        "2017-18",
        "2018-19",
        "2021-22",
        "2022-23",
        "2023-24",
        "2024-25",
    ]

    # Check which ones are currently being processed or completed
    data_dir = "data/player_box_scores"

    missing_seasons = []
    for season in all_seasons:
        file_path = f"{data_dir}/nba_player_games_{season}.csv"
        if not os.path.exists(file_path):
            missing_seasons.append(season)

    return missing_seasons


def run_backfill_season(season):
    """Run backfill for a specific season"""

    print(f"\n🚀 Starting backfill for {season}...")

    cmd = [sys.executable, "add_new_players.py", "--seasons", season, "--delay", "3.0"]

    try:
        # Run in background and return immediately
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        print(f"   ✅ {season} collection started (PID: {process.pid})")
        return process

    except Exception as e:
        print(f"   ❌ Failed to start {season}: {e}")
        return None


def main():
    """Main backfill orchestrator"""

    print("🔄 NBA HISTORICAL BACKFILL FOR 15 NEW PLAYERS")
    print("=" * 55)

    missing_seasons = get_missing_seasons()

    if not missing_seasons:
        print("✅ All seasons appear to have been processed!")
        return

    print(f"📋 Seasons needing backfill: {missing_seasons}")
    print("👥 Adding 15 new players to each season")
    print("⏱️ Using conservative 3.0s API delays")

    # Process seasons in chunks to avoid overwhelming the API
    chunk_size = 3  # Process 3 seasons at a time

    for i in range(0, len(missing_seasons), chunk_size):
        chunk = missing_seasons[i : i + chunk_size]

        print(f"\n📦 Processing chunk {i // chunk_size + 1}: {chunk}")

        processes = []
        for season in chunk:
            process = run_backfill_season(season)
            if process:
                processes.append((season, process))
                time.sleep(5)  # Small delay between starting each process

        if processes:
            print("⏳ Waiting for chunk to complete before starting next...")

            # Wait for all processes in this chunk to complete
            for season, process in processes:
                try:
                    stdout, stderr = process.communicate(
                        timeout=1800
                    )  # 30 minute timeout
                    if process.returncode == 0:
                        print(f"   ✅ {season} completed successfully")
                    else:
                        print(
                            f"   ⚠️ {season} completed with issues (code: {process.returncode})"
                        )
                        if stderr:
                            print(f"      Error: {stderr[:200]}...")
                except subprocess.TimeoutExpired:
                    print(f"   ⏰ {season} timed out after 30 minutes")
                    process.kill()
                except Exception as e:
                    print(f"   ❌ {season} error: {e}")

            # Pause between chunks
            if i + chunk_size < len(missing_seasons):
                print("⏸️ Pausing 2 minutes between chunks...")
                time.sleep(120)

    print("\n🏁 BACKFILL COMPLETE!")
    print(f"📊 Processed {len(missing_seasons)} seasons")
    print("🎯 Each season should now have 45 total players (30 original + 15 new)")


if __name__ == "__main__":
    main()
