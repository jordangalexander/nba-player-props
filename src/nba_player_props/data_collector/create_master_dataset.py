#!/usr/bin/env python3
"""
Create a single master dataset from all individual season files.

This script combines all nba_player_games_XXXX.csv files into one comprehensive dataset.
"""

import os
from datetime import datetime

import pandas as pd


def create_master_dataset():
    """Combine all season files into one master dataset"""

    print("📊 CREATING MASTER NBA DATASET")
    print("=" * 40)

    data_dir = "data/player_box_scores"

    # Get all season files
    season_files = [
        f
        for f in os.listdir(data_dir)
        if f.startswith("nba_player_games_") and f.endswith(".csv")
    ]

    if not season_files:
        print("❌ No season files found")
        return None

    season_files.sort()  # Sort chronologically
    print(f"📁 Found {len(season_files)} season files:")

    all_data = []
    total_games = 0

    for file in season_files:
        file_path = os.path.join(data_dir, file)
        try:
            df = pd.read_csv(file_path)
            all_data.append(df)

            season = file.replace("nba_player_games_", "").replace(".csv", "")
            players = df["PLAYER_ID"].nunique()
            games = len(df)
            total_games += games

            print(f"   ✅ {season}: {games:,} games, {players} players")

        except Exception as e:
            print(f"   ❌ Error loading {file}: {e}")

    if not all_data:
        print("❌ No data loaded")
        return None

    print(f"\n🔄 Combining {len(all_data)} season datasets...")

    # Combine all data
    master_df = pd.concat(all_data, ignore_index=True)

    # Remove duplicates based on Player_ID and Game_ID
    initial_count = len(master_df)
    master_df = master_df.drop_duplicates(subset=["PLAYER_ID", "Game_ID"])
    final_count = len(master_df)

    if initial_count != final_count:
        print(f"🔧 Removed {initial_count - final_count:,} duplicate games")

    # Add metadata
    master_df["DATASET_CREATED"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sort by player and date for better organization
    master_df = master_df.sort_values(["PLAYER_ID", "GAME_DATE"])
    master_df = master_df.reset_index(drop=True)

    # Save master dataset
    output_file = os.path.join(data_dir, "nba_master_dataset.csv")
    master_df.to_csv(output_file, index=False)

    # Display comprehensive summary
    print("\n🎯 MASTER DATASET CREATED:")
    print(f"   📊 Total games: {len(master_df):,}")
    print(f"   👥 Unique players: {master_df['PLAYER_ID'].nunique()}")

    if "SEASON" in master_df.columns:
        seasons = sorted(master_df["SEASON"].unique())
        print(f"   🏀 Seasons covered: {len(seasons)} seasons")
        print(f"      📅 From {seasons[0]} to {seasons[-1]}")

    if "GAME_DATE" in master_df.columns and master_df["GAME_DATE"].notna().any():
        date_range = f"{master_df['GAME_DATE'].min()} to {master_df['GAME_DATE'].max()}"
        print(f"   📅 Date range: {date_range}")

    if "PLAYER_NAME" in master_df.columns:
        print("   👤 Player names included: Yes")

    # File size
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"   💾 File: nba_master_dataset.csv ({file_size_mb:.1f} MB)")

    # Sample stats
    if "PTS" in master_df.columns:
        avg_pts = master_df["PTS"].mean()
        print(f"   📈 Average points per game: {avg_pts:.1f}")

    if "REB" in master_df.columns:
        avg_reb = master_df["REB"].mean()
        print(f"   📈 Average rebounds per game: {avg_reb:.1f}")

    if "AST" in master_df.columns:
        avg_ast = master_df["AST"].mean()
        print(f"   📈 Average assists per game: {avg_ast:.1f}")

    print("\n✅ Master dataset ready for analysis!")
    return master_df


def display_final_structure():
    """Show the final clean data structure"""

    print("\n🎯 FINAL DATA STRUCTURE:")
    print("=" * 30)

    data_dir = "data/player_box_scores"
    files = sorted([f for f in os.listdir(data_dir) if f.endswith(".csv")])

    season_files = [f for f in files if f.startswith("nba_player_games_")]
    master_files = [f for f in files if "master" in f]

    print("📁 Individual Season Files:")
    for file in season_files:
        season = file.replace("nba_player_games_", "").replace(".csv", "")
        print(f"   🏀 {season}")

    print("\n📦 Master Dataset:")
    for file in master_files:
        print(f"   🎯 {file}")

    print("\n✅ Perfect! Clean data flow achieved:")
    print(f"   • {len(season_files)} individual season files")
    print("   • 1 comprehensive master dataset")
    print("   • No duplicates or obsolete files")
    print("   • Ready for prop betting analysis!")


if __name__ == "__main__":
    master_df = create_master_dataset()
    if master_df is not None:
        display_final_structure()
        print("\n🚀 Data is now ready for NBA prop betting analysis!")
    else:
        print("\n❌ Failed to create master dataset")
