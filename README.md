# NBA Player Props

A Python library for retrieving NBA data, performing statistical analysis, and predicting outcomes for NBA player prop bets.

## Features

- **Data Collection**: Retrieve NBA player statistics and game logs from various sources
- **Statistical Analysis**: Analyze player performance, trends, and matchup data
- **Prediction Models**: Machine learning models to predict player prop bet outcomes
- **Type Safety**: Full type hints and mypy compatibility
- **Testing**: Comprehensive test suite with pytest

## Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for fast package management
- [tox](https://tox.wiki/) for testing and linting

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jordangalexander/nba-player-props.git
cd nba-player-props
```

2. Install dependencies:
```bash
pip install uv tox
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
uv pip install -e .
```

## Development

### Testing

Run tests with Python 3.12:
```bash
tox -e py312
```

Run all tests:
```bash
tox
```

### Linting and Formatting

Fix linting issues automatically:
```bash
tox -e fix_lint
```

Check linting without fixing:
```bash
tox -e lint
```

This will run:
- `ruff format` for code formatting
- `ruff check --fix` for linting fixes
- `mypy` for type checking

### Project Structure

```
nba-player-props/
├── src/
│   └── nba_player_props/
│       ├── __init__.py
│       ├── data_collector/
│       │   ├── __init__.py
│       │   ├── data_collector.py    # Core data collection module
│       │   └── collect_nba_data.py  # Advanced collection utilities
│       ├── analyzer.py              # Statistical analysis
│       └── predictor.py             # ML prediction models
├── data/
│   └── player_box_scores/          # Season CSV files
├── notebooks/                       # Jupyter notebooks for analysis
├── tests/                          # Test suite
├── update_data.py                  # 🎯 Main updater (use this!)
├── flexible_collect.py             # Advanced collection tool
├── recommend_players.py            # Player recommendation analysis
├── requirements.txt               # Core dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                # Project configuration
└── tox.ini                       # Testing configuration
```

**Key Scripts:**
- **`update_data.py`** - Your go-to script for keeping data current ⭐
- **`flexible_collect.py`** - Advanced data collection with full control
- **`recommend_players.py`** - Analyze and recommend players for prop betting

## Usage

### 🎯 Quick Start - Update Current Season Data

The easiest way to keep your data current:

```bash
# Check what data you have
python update_data.py --check

# Update all tracked players for current season (auto-detected)
python update_data.py

# Update specific player list
python update_data.py --players original_30
```

**That's it!** The script auto-detects the current season and updates through today.

### 📊 Data Collection Scripts

We have two main scripts for data collection:

1. **`update_data.py`** - Smart updater (recommended for regular use)
   - Auto-detects current season
   - Checks existing data
   - Updates through today
   - Simple and fast

2. **`flexible_collect.py`** - Advanced control (for specific needs)
   - Collect specific players
   - Target specific seasons or date ranges
   - Custom player lists
   - More control over the process

### 🚀 Common Use Cases

#### Update Current Season
```bash
# Update all tracked players (60 players total)
python update_data.py

# Just the core 30 superstars
python update_data.py --players original_30
```

#### Check Data Status
```bash
python update_data.py --check
```

This shows:
- What seasons you have data for
- How many games and players per season
- When data was last updated
- If current season needs updating

#### Backfill Historical Data
```bash
# Update a specific past season
python update_data.py --season 2023-24

# Or use flexible_collect for range
python flexible_collect.py --players original_30 --start 2020 --end 2024
```

#### Custom Player Lists
```bash
# Available lists: original_30, second_wave_15, third_wave_15
python flexible_collect.py --players second_wave_15 --seasons 2024-25

# Or provide comma-separated names
python flexible_collect.py --players "LeBron James,Stephen Curry,Nikola Jokic" --seasons 2024-25
```

### 🐍 Python API Usage

```python
from nba_player_props.data_collector import DataCollector

# Initialize collector
collector = DataCollector()

# Get single player data
lebron_data = collector.get_player_data_by_name(
    "LeBron James", 
    seasons=["2024-25", "2023-24"]
)

print(f"Collected {len(lebron_data)} games")
print(f"Average points: {lebron_data['PTS'].mean():.1f}")

# Get multiple players efficiently
player_ids = [2544, 201939, 203507]  # LeBron, Curry, Giannis
all_data = collector.collect_multiple_players(
    player_ids, 
    seasons=["2024-25"],
    include_playoffs=False
)
```

### 📁 Data Files

Data is saved to `data/player_box_scores/`:
- `nba_player_games_2024-25.csv` - Current season
- `nba_player_games_2023-24.csv` - Previous seasons
- etc.

Each file contains:
- Player box score stats (PTS, REB, AST, etc.)
- Game metadata (date, matchup, W/L)
- Season identifiers
- Player IDs and names

## Configuration

The project uses `pyproject.toml` for configuration. Key settings:

- **Ruff**: Code linting and formatting
- **MyPy**: Type checking with strict settings
- **Pytest**: Test configuration with coverage reporting
- **Tox**: Multi-environment testing with uv

## Contributing

1. Ensure tests pass: `tox -e py312`
2. Fix linting issues: `tox -e fix_lint`
3. Add tests for new features
4. Update documentation as needed

## License

MIT License - see LICENSE file for details.
