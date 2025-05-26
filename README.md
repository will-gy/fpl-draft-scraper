# FPL Draft Scraper

A Python-based scraper for the Official Premier League Draft Fantasy Football game that provides insights into player ownership, draft patterns, and H2H expected points (xPts) calculations.

## Features

- League ID and Size Collection
- Premier League Player Data Management
- Average Draft Position Analysis
- Expected Points (xPts) Table Generation
- Weekly Waiver Analysis
- Player Ownership Statistics

## Setup and Usage

### Prerequisites

- Python 3.x
- Required packages (install via pip):
  - aiohttp
  - asyncio
  - pandas
  - plotly

### Initial Setup

1. **League Data Collection** (`scrape_leagueid_main.py`)
   - Run this script at the beginning of the season
   - Collects a sample of league IDs and their sizes
   - Recommended sample size: 50,000+ leagues (especially if calculating metrics for larger league sizes)
   - Populates the "league" table in SQLite database

2. **Player Database Setup** (`scrape_players_main.py`)
   - Run initially at season start
   - Updates database with current Premier League players
   - Stores player ID, name, position, and official draft rank
   - Can be run periodically to capture new players added

### Regular Usage

#### Draft Analysis (`draft_main.py`)
- Analyzes draft patterns across collected leagues
- Generates report showing average draft position for each player in dataset
- Only includes leagues where drafts have been completed

#### Expected Points Table (`xpts_table_main.py`)
- Input: H2H League ID
- Output: "xPts" table showing:
  - Current league standings
  - Expected points based on team performance
  - Useful for analyzing team strength and luck factor

#### Weekly Ownership Analysis (`calc_ownership_main.py`)
- Primary weekly analysis tool
- Inputs:
  - Current gameweek
  - Target league size
  - Your league ID
- Outputs:
  - Most commonly added/dropped players
  - Ownership percentages across similar-sized leagues
  - Availability status in your league

## Data Flow

1. League ID collection (`scrape_leagueid_main.py`) → "leagues" table in SQLite database
2. Player data collection (`scrape_players_main.py`) → "player" table in SQLLite database
3. Weekly analysis using collected league IDs (`calc_ownership_main.py`/`xpts_table_main.py`)
4. Report generation based on user parameters

## Best Practices

- Run league ID collection at season start with large sample size
- Update player database weekly or after transfer windows
- Generate ownership reports weekly post-waiver deadline to decide which players to target on free transfers
