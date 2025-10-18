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

```python
from nba_player_props import DataCollector, PlayerAnalyzer, PropPredictor

# Collect player data
collector = DataCollector()
player_stats = collector.get_player_stats(player_id=1234, season="2023-24")
game_logs = collector.get_game_logs(player_id=1234, season="2023-24")

# Analyze performance
analyzer = PlayerAnalyzer()
averages = analyzer.calculate_averages(game_logs, rolling_window=10)
matchup_analysis = analyzer.analyze_matchup(player_stats, opponent="LAL")

# Predict prop outcomes
predictor = PropPredictor()
predictor.train_model(player_stats, target_stat="points")
over_prob, under_prob = predictor.predict_prop(player_stats, prop_line=25.5)
recommendation = predictor.get_recommendation(player_stats, prop_line=25.5)
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
