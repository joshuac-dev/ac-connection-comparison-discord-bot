# Airline Network Optimizer Discord Bot

A Discord bot that helps you find optimal airports for your airline network in Airline Club. The bot analyzes airports based on population, income, competition, and distance from your headquarters to calculate a Base Opportunity Score (BOS).

## Features

- `/network-run` - Find the best airports for your airline network
- Filters airports by country openness and distance
- Calculates competition from existing routes
- Scores airports using Base Opportunity Score (BOS) formula
- Concurrent API calls with rate limiting
- In-memory caching for improved performance

## Requirements

- Python 3.9 or higher
- Discord Bot Token

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- discord.py (Discord API wrapper)
- aiohttp (Async HTTP client)
- pandas (Data manipulation)
- numpy (Numerical operations)
- python-dotenv (Environment variable management)

### 2. Set Up Discord Bot Token

Create a `.env` file in the project root:

```bash
DISCORD_TOKEN=your_discord_bot_token_here
```

Or set the environment variable directly:

```bash
export DISCORD_TOKEN=your_discord_bot_token_here
```

**How to get a Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the token (keep it secret!)
5. Enable "Message Content Intent" in the Bot settings
6. Invite the bot to your server with appropriate permissions

### 3. Run the Bot

```bash
python bot.py
```

The bot will start and sync slash commands with Discord. You should see:
```
Syncing slash commands...
Slash commands synced!
Bot logged in as YourBot#1234 (ID: 123456789)
------
```

## Usage

### `/network-run` Command

Find optimal airports for your airline network.

**Arguments:**
- `hq_code` (required): IATA code of your headquarters airport (e.g., LAX, JFK, LHR)
- `min_openness` (optional): Minimum country openness level (0-10, default: 0)
- `max_distance` (optional): Maximum distance from HQ in kilometers (default: 20000)

**Example:**

```
/network-run hq_code:JFK min_openness:5 max_distance:5000
```

This will find the top 15 airports within 5000 km of JFK in countries with openness ≥ 5.

**Output:**

The bot returns a formatted table with:
- **Rank**: Position in the sorted list
- **IATA**: Airport IATA code
- **Name**: Airport name (truncated to 22 characters)
- **CC(Open)**: Country code and openness level
- **Dist(km)**: Distance from HQ in kilometers
- **Pop**: Airport population
- **Income**: Airport income level
- **CompSeats**: Total competition seats (sum of link capacities)
- **BOS**: Base Opportunity Score (higher is better)

## How It Works

### Base Opportunity Score (BOS) Formula

The bot calculates BOS for each airport using:

```
distance_factor = 0.1 if distance < 200km
                  1.5 if 200km ≤ distance ≤ 2000km
                  1.0 if distance > 2000km

competition_score = competition_seats / 10000

BOS = (Population^0.7 × Income^1.3) / (1 + competition_score)^1.5 × distance_factor
```

### Execution Flow

1. **Phase A - Data Collection & Filtering:**
   - Fetches countries and airports from Airline Club API
   - Locates your HQ airport by IATA code
   - Filters airports by openness and distance using Haversine formula

2. **Phase B - Competition Analysis:**
   - Fetches existing routes for each filtered airport (max 20 concurrent requests)
   - Sums capacity of all links to calculate competition

3. **Phase C - Scoring & Ranking:**
   - Calculates BOS for each airport
   - Sorts by BOS (descending)
   - Returns top 15 results

### Caching

The bot caches country and airport data for 10 minutes to improve performance and reduce API load.

## Project Structure

```
.
├── bot.py                 # Main entrypoint
├── cogs/
│   ├── __init__.py
│   └── network.py         # /network-run command implementation
├── utils/
│   ├── __init__.py
│   ├── http.py            # HTTP client with caching
│   ├── geo.py             # Haversine distance calculation
│   └── scoring.py         # BOS calculation logic
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## Development

### Architecture

- **Modular Design**: Separate utilities for HTTP, geography, and scoring
- **Async/Await**: Fully asynchronous using aiohttp and discord.py
- **Type Hints**: Type annotations throughout for better IDE support
- **Graceful Error Handling**: Timeout handling, API failures, and user errors
- **Rate Limiting**: Semaphore-based concurrency control (max 20 concurrent requests)

### Testing

To test the bot:
1. Ensure you have a valid Discord bot token
2. Invite the bot to a test server
3. Run the bot with `python bot.py`
4. Use `/network-run` with various parameters

## Troubleshooting

**Bot doesn't respond to commands:**
- Make sure slash commands are synced (check console output)
- Verify the bot has appropriate permissions in your server
- Try waiting a few minutes for Discord to propagate commands

**"Failed to fetch data" error:**
- Check your internet connection
- Verify Airline Club API is accessible
- The API might be temporarily down

**Token errors:**
- Ensure DISCORD_TOKEN is set correctly
- Verify the token is valid in Discord Developer Portal
- Make sure you didn't accidentally share your token

## License

This bot is provided as-is for use with Airline Club game.

## Credits

Data provided by [Airline Club](https://www.airline-club.com)
