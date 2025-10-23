#!/usr/bin/env python3
"""
NBA Player Recommendation System for Prop Betting Data Collection

This script analyzes various factors to recommend the next 15 players
to add to our dataset based on prop betting value and data availability.
"""

import os
import sys

import pandas as pd

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from nba_player_props.data_collector.data_collector import DataCollector


def get_current_players():
    """Get the list of all 45 players we currently have data for"""

    return [
        # Core superstars (original 30)
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
        # Second wave additions (15 players added)
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


def get_prop_betting_criteria():
    """Define criteria for valuable prop betting players"""

    return {
        "scoring_volume": {
            "min_ppg": 15.0,
            "weight": 0.25,
            "description": "Points per game (15+ for regular point props)",
        },
        "rebounding_volume": {
            "min_rpg": 6.0,
            "weight": 0.15,
            "description": "Rebounds per game (6+ for rebound props)",
        },
        "assist_volume": {
            "min_apg": 4.0,
            "weight": 0.15,
            "description": "Assists per game (4+ for assist props)",
        },
        "minutes_played": {
            "min_mpg": 25.0,
            "weight": 0.20,
            "description": "Minutes per game (25+ for consistent stats)",
        },
        "games_played": {
            "min_games": 50,
            "weight": 0.15,
            "description": "Games played in recent season (50+ for reliability)",
        },
        "market_interest": {
            "all_star": 3.0,
            "rising_star": 2.0,
            "veteran": 1.5,
            "weight": 0.10,
            "description": "Market interest level (All-Star > Rising Star > Veteran)",
        },
    }


def analyze_recent_season_stats():
    """Analyze 2023-24 season stats to identify top candidates"""

    print("📊 ANALYZING 2023-24 SEASON STATISTICS")
    print("=" * 50)

    collector = DataCollector()

    try:
        # Get all active players from 2023-24 season
        active_players = collector.get_active_players("2023-24")

        if active_players.empty:
            print("❌ Could not retrieve active players data")
            return pd.DataFrame()

        print(f"✅ Found {len(active_players)} active players in 2023-24")

        # For efficiency, we'll focus on players who played significant minutes
        # and exclude our current 30 players
        current_players = get_current_players()

        # Third wave candidates (excluding all 45 players we already have)
        candidate_players = [
            # Elite players we still don't have
            {
                "name": "Nikola Vucevic",
                "ppg": 18.0,
                "rpg": 10.5,
                "apg": 3.2,
                "mpg": 32.8,
                "games": 76,
                "tier": "veteran",
            },
            {
                "name": "Fred VanVleet",
                "ppg": 17.4,
                "rpg": 3.8,
                "apg": 8.1,
                "mpg": 36.9,
                "games": 73,
                "tier": "veteran",
            },
            {
                "name": "Terry Rozier",
                "ppg": 16.4,
                "rpg": 4.2,
                "apg": 3.7,
                "mpg": 31.7,
                "games": 68,
                "tier": "veteran",
            },
            {
                "name": "Myles Turner",
                "ppg": 17.1,
                "rpg": 6.9,
                "apg": 1.9,
                "mpg": 29.8,
                "games": 77,
                "tier": "veteran",
            },
            {
                "name": "Kristaps Porzingis",
                "ppg": 20.1,
                "rpg": 7.2,
                "apg": 2.0,
                "mpg": 29.5,
                "games": 57,
                "tier": "all_star",
            },
            # Rising stars and key role players
            {
                "name": "Nic Claxton",
                "ppg": 11.8,
                "rpg": 9.9,
                "apg": 2.1,
                "mpg": 25.9,
                "games": 71,
                "tier": "rising_star",
            },
            {
                "name": "Jaden McDaniels",
                "ppg": 10.9,
                "rpg": 3.9,
                "apg": 2.0,
                "mpg": 28.4,
                "games": 79,
                "tier": "rising_star",
            },
            {
                "name": "OG Anunoby",
                "ppg": 14.7,
                "rpg": 4.2,
                "apg": 2.5,
                "mpg": 32.8,
                "games": 50,
                "tier": "rising_star",
            },
            {
                "name": "Jerami Grant",
                "ppg": 21.0,
                "rpg": 3.9,
                "apg": 2.4,
                "mpg": 33.0,
                "games": 54,
                "tier": "veteran",
            },
            {
                "name": "Tobias Harris",
                "ppg": 17.2,
                "rpg": 6.5,
                "apg": 3.1,
                "mpg": 32.7,
                "games": 70,
                "tier": "veteran",
            },
            {
                "name": "Jalen Williams",
                "ppg": 19.1,
                "rpg": 4.0,
                "apg": 4.5,
                "mpg": 29.3,
                "games": 71,
                "tier": "rising_star",
            },
            {
                "name": "Ausar Thompson",
                "ppg": 8.8,
                "rpg": 6.4,
                "apg": 4.9,
                "mpg": 25.1,
                "games": 63,
                "tier": "rising_star",
            },
            {
                "name": "Isaiah Hartenstein",
                "ppg": 7.8,
                "rpg": 8.3,
                "apg": 2.5,
                "mpg": 25.3,
                "games": 75,
                "tier": "veteran",
            },
            {
                "name": "Jonas Valanciunas",
                "ppg": 12.2,
                "rpg": 8.8,
                "apg": 2.1,
                "mpg": 23.5,
                "games": 82,
                "tier": "veteran",
            },
            {
                "name": "Clint Capela",
                "ppg": 11.5,
                "rpg": 10.6,
                "apg": 1.5,
                "mpg": 29.3,
                "games": 77,
                "tier": "veteran",
            },
            {
                "name": "Tim Hardaway Jr.",
                "ppg": 14.4,
                "rpg": 3.2,
                "apg": 1.8,
                "mpg": 27.1,
                "games": 79,
                "tier": "veteran",
            },
            {
                "name": "Cam Thomas",
                "ppg": 22.5,
                "rpg": 3.2,
                "apg": 2.9,
                "mpg": 28.8,
                "games": 66,
                "tier": "rising_star",
            },
            {
                "name": "Immanuel Quickley",
                "ppg": 18.6,
                "rpg": 4.8,
                "apg": 6.8,
                "mpg": 32.3,
                "games": 38,
                "tier": "rising_star",
            },
            {
                "name": "Trey Murphy III",
                "ppg": 14.8,
                "rpg": 4.9,
                "apg": 2.2,
                "mpg": 30.8,
                "games": 57,
                "tier": "rising_star",
            },
            {
                "name": "Keyonte George",
                "ppg": 13.0,
                "rpg": 3.0,
                "apg": 4.4,
                "mpg": 25.8,
                "games": 75,
                "tier": "rising_star",
            },
            {
                "name": "Walker Kessler",
                "ppg": 8.1,
                "rpg": 7.5,
                "apg": 2.4,
                "mpg": 23.3,
                "games": 64,
                "tier": "rising_star",
            },
            {
                "name": "Gradey Dick",
                "ppg": 8.5,
                "rpg": 2.9,
                "apg": 1.8,
                "mpg": 20.0,
                "games": 60,
                "tier": "rising_star",
            },
            {
                "name": "Jaime Jaquez Jr.",
                "ppg": 11.9,
                "rpg": 3.8,
                "apg": 2.6,
                "mpg": 28.2,
                "games": 70,
                "tier": "rising_star",
            },
        ]

        # Filter out players we already have
        filtered_candidates = []
        for player in candidate_players:
            if player["name"] not in current_players:
                filtered_candidates.append(player)

        candidates_df = pd.DataFrame(filtered_candidates)
        return candidates_df

    except Exception as e:
        print(f"❌ Error analyzing season stats: {e}")
        return pd.DataFrame()


def calculate_prop_value_score(player_stats, criteria):
    """Calculate a prop betting value score for a player"""

    score = 0.0
    breakdown = {}

    # Scoring volume
    ppg_score = min(player_stats["ppg"] / 30.0, 1.0)  # Normalize to 30 PPG max
    score += ppg_score * criteria["scoring_volume"]["weight"]
    breakdown["scoring"] = ppg_score * criteria["scoring_volume"]["weight"]

    # Rebounding volume
    rpg_score = min(player_stats["rpg"] / 15.0, 1.0)  # Normalize to 15 RPG max
    score += rpg_score * criteria["rebounding_volume"]["weight"]
    breakdown["rebounding"] = rpg_score * criteria["rebounding_volume"]["weight"]

    # Assist volume
    apg_score = min(player_stats["apg"] / 12.0, 1.0)  # Normalize to 12 APG max
    score += apg_score * criteria["assist_volume"]["weight"]
    breakdown["assists"] = apg_score * criteria["assist_volume"]["weight"]

    # Minutes played (consistency indicator)
    mpg_score = min(player_stats["mpg"] / 40.0, 1.0)  # Normalize to 40 MPG max
    score += mpg_score * criteria["minutes_played"]["weight"]
    breakdown["minutes"] = mpg_score * criteria["minutes_played"]["weight"]

    # Games played (availability/health)
    games_score = min(player_stats["games"] / 82.0, 1.0)  # Normalize to 82 games max
    score += games_score * criteria["games_played"]["weight"]
    breakdown["availability"] = games_score * criteria["games_played"]["weight"]

    # Market interest tier
    tier_scores = {
        "all_star": criteria["market_interest"]["all_star"],
        "rising_star": criteria["market_interest"]["rising_star"],
        "veteran": criteria["market_interest"]["veteran"],
    }
    tier_score = tier_scores.get(player_stats["tier"], 1.0) / 3.0  # Normalize
    score += tier_score * criteria["market_interest"]["weight"]
    breakdown["market_interest"] = tier_score * criteria["market_interest"]["weight"]

    return score, breakdown


def rank_candidates(candidates_df):
    """Rank candidate players by prop betting value"""

    print("\n🏆 RANKING CANDIDATES BY PROP BETTING VALUE")
    print("=" * 50)

    criteria = get_prop_betting_criteria()

    # Calculate scores for each candidate
    scores = []
    for _, player in candidates_df.iterrows():
        score, breakdown = calculate_prop_value_score(player, criteria)
        scores.append(
            {
                "name": player["name"],
                "score": score,
                "tier": player["tier"],
                "ppg": player["ppg"],
                "rpg": player["rpg"],
                "apg": player["apg"],
                "mpg": player["mpg"],
                "games": player["games"],
                "breakdown": breakdown,
            }
        )

    # Sort by score descending
    scores.sort(key=lambda x: x["score"], reverse=True)

    # Display rankings
    print("📋 TOP CANDIDATES (showing score breakdown):")
    print()

    for i, player in enumerate(scores[:20], 1):  # Show top 20
        name = player["name"]
        score = player["score"]
        tier = player["tier"].title()

        print(f"{i:2d}. {name:<20} (Score: {score:.3f}) [{tier}]")
        print(
            f"    📊 {player['ppg']:.1f} PPG, {player['rpg']:.1f} RPG, {player['apg']:.1f} APG"
        )
        print(f"    ⏰ {player['mpg']:.1f} MPG, {player['games']} games")
        print()

    return scores


def recommend_next_15(ranked_candidates):
    """Recommend the top 15 players for data collection"""

    print("🎯 RECOMMENDED NEXT 15 PLAYERS FOR DATA COLLECTION")
    print("=" * 55)

    top_15 = ranked_candidates[:15]

    print("✅ PRIMARY RECOMMENDATIONS:")
    for i, player in enumerate(top_15, 1):
        name = player["name"]
        score = player["score"]
        tier = player["tier"].title()

        # Create justification based on strengths
        strengths = []
        if player["ppg"] >= 20:
            strengths.append(f"High scoring ({player['ppg']:.1f} PPG)")
        if player["rpg"] >= 8:
            strengths.append(f"Strong rebounds ({player['rpg']:.1f} RPG)")
        if player["apg"] >= 6:
            strengths.append(f"Good assists ({player['apg']:.1f} APG)")
        if player["games"] >= 70:
            strengths.append("High availability")
        if player["tier"] == "all_star":
            strengths.append("All-Star level")

        justification = ", ".join(strengths[:3])  # Top 3 strengths

        print(f"{i:2d}. {name:<20} [{tier}]")
        print(f"    Score: {score:.3f} | {justification}")
        print(
            f"    Stats: {player['ppg']:.1f} PPG, {player['rpg']:.1f} RPG, {player['apg']:.1f} APG"
        )
        print()

    # Create categories for collection strategy
    all_stars = [p for p in top_15 if p["tier"] == "all_star"]
    rising_stars = [p for p in top_15 if p["tier"] == "rising_star"]
    veterans = [p for p in top_15 if p["tier"] == "veteran"]

    print("📈 COLLECTION STRATEGY:")
    print(f"   🌟 All-Stars: {len(all_stars)} players (highest priority)")
    print(f"   🚀 Rising Stars: {len(rising_stars)} players (high growth potential)")
    print(f"   🏀 Veterans: {len(veterans)} players (consistent performers)")

    print("\n💡 RATIONALE:")
    print("   • Prioritizes players with multiple prop betting categories")
    print("   • Balances star power with statistical volume")
    print("   • Considers availability and consistency")
    print("   • Focuses on players likely to have betting markets")

    # Return list of names for easy copying
    return [player["name"] for player in top_15]


def export_recommendations(top_15_names):
    """Export recommendations in a format ready for code integration"""

    print("\n📝 CODE-READY EXPORT:")
    print("=" * 25)

    print("# Add these 15 players to expand to 45 total players:")
    print("next_15_players = [")
    for name in top_15_names:
        print(f'    "{name}",')
    print("]")

    print("\n# Combined list (current 30 + next 15 = 45 total):")
    current = get_current_players()
    print("all_45_players = [")
    print("    # Current 30 players")
    for name in current:
        print(f'    "{name}",')
    print("    # Next 15 recommended players")
    for name in top_15_names:
        print(f'    "{name}",')
    print("]")


def main():
    """Main analysis function"""

    print("🔍 NBA PLAYER RECOMMENDATION SYSTEM")
    print("🎯 Goal: Identify next 15 players for prop betting dataset")
    print("=" * 60)

    # Get current players
    current_players = get_current_players()
    print(f"📊 Current dataset: {len(current_players)} players")

    # Analyze candidates
    candidates_df = analyze_recent_season_stats()

    if candidates_df.empty:
        print("❌ Could not analyze candidate players")
        return

    print(f"🔍 Analyzing {len(candidates_df)} candidate players...")

    # Rank candidates
    ranked_candidates = rank_candidates(candidates_df)

    # Make recommendations
    top_15_names = recommend_next_15(ranked_candidates)

    # Export for easy integration
    export_recommendations(top_15_names)

    print("\n🎉 ANALYSIS COMPLETE!")
    print("✅ Recommended 15 players to expand dataset to 45 total players")
    print("🚀 Ready to run data collection for these new targets!")


if __name__ == "__main__":
    main()
