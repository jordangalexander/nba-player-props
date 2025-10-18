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
│       ├── data_collector.py    # NBA data retrieval
│       ├── analyzer.py          # Statistical analysis
│       └── predictor.py         # ML prediction models
├── tests/                       # Test suite
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Project configuration
├── tox.ini                    # Testing configuration
└── README.md
```

## Usage

### Quick Start - Single Player Data
```python
from nba_player_props import DataCollector

# Initialize collector
collector = DataCollector()

# Get LeBron James data for recent seasons
lebron_data = collector.get_player_data_by_name(
    "LeBron James", 
    seasons=["2022-23", "2023-24"]
)

print(f"Collected {len(lebron_data)} games")
print(f"Average points: {lebron_data['PTS'].mean():.1f}")
```

### Comprehensive Data Collection
```python
# Run the comprehensive collection script
python example_usage.py

# This will:
# 1. Collect ALL NBA players from 2010-present
# 2. Include regular season + playoffs
# 3. Save results to CSV file
# 4. Handle rate limiting and errors automatically
```

### Advanced Usage - Multiple Players
```python
from nba_player_props import DataCollector

collector = DataCollector()

# Get all active players
active_players = collector.get_active_players()
player_ids = active_players['PERSON_ID'].head(10).tolist()

# Collect data for multiple players efficiently
all_data = collector.collect_multiple_players(
    player_ids, 
    seasons=["2023-24"],
    include_playoffs=True
)

# Results include:
# - PLAYER_ID, SEASON, SEASON_TYPE
# - All standard box score stats (PTS, REB, AST, etc.)
# - Game metadata (GAME_DATE, MATCHUP, etc.)
```

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
