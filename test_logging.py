"""Simple test script to verify logging is working."""

import logging
import sys

sys.path.append("src")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from nba_player_props.data_collector import DataCollector


def test_logging():
    """Test that logging is working in DataCollector."""
    print("Testing DataCollector with logging...")

    collector = DataCollector()

    # Test getting seasons (should log info if cache is empty)
    seasons = collector.get_seasons_list(start_year=2023)
    print(f"Generated seasons: {seasons}")

    # Test with invalid player name (should log info)
    result = collector.get_player_data_by_name("Invalid Player Name")
    print(f"Invalid player result: {len(result)} games")

    print("Logging test completed successfully!")


if __name__ == "__main__":
    test_logging()
