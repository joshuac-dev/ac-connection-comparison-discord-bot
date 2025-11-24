# Airline Network Optimizer Discord Bot

A Discord bot that helps you find optimal airports for your airline network in Airline Club. The bot analyzes airports based on population, income, competition, and distance from your headquarters to calculate a Base Opportunity Score (BOS).

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Complete Setup Guide for Beginners](#complete-setup-guide-for-beginners)
  - [Step 1: Install Python](#step-1-install-python)
  - [Step 2: Download the Bot Code](#step-2-download-the-bot-code)
  - [Step 3: Install Python Dependencies](#step-3-install-python-dependencies)
  - [Step 4: Create Your Discord Bot](#step-4-create-your-discord-bot)
  - [Step 5: Configure the Bot Token](#step-5-configure-the-bot-token)
  - [Step 6: Run the Bot](#step-6-run-the-bot)
  - [Step 7: Use the Bot](#step-7-use-the-bot)
- [Usage Examples](#usage-examples)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Advanced Setup (Optional)](#advanced-setup-optional)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
- [Troubleshooting](#troubleshooting)
- [For Developers](#for-developers)

## Features

- `/network-run` - Find the best airports for your airline network
- Filters airports by country openness and distance
- Calculates competition from existing routes
- Scores airports using Base Opportunity Score (BOS) formula
- Concurrent API calls with rate limiting
- In-memory caching for improved performance

## Requirements

- **Python 3.9 or higher** (Python 3.10+ recommended)
- **Discord Account** with permissions to create applications
- **A Discord Server** where you can add the bot (create one if needed)
- **Internet connection** to access Discord and Airline Club APIs

## Complete Setup Guide for Beginners

### Step 1: Install Python

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing:
   ```bash
   python --version
   ```
   You should see something like `Python 3.12.3`

**macOS:**
1. Install using Homebrew (recommended):
   ```bash
   brew install python3
   ```
   Or download from [python.org/downloads](https://www.python.org/downloads/)
2. Verify installation:
   ```bash
   python3 --version
   ```

**Linux:**
```bash
# Ubuntu/Debian (install python3-venv for virtual environment support)
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-full

# Fedora
sudo dnf install python3 python3-pip

# Verify installation
python3 --version
```

### Step 2: Download the Bot Code

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/joshuac-dev/ac-connection-comparison-discord-bot.git
cd ac-connection-comparison-discord-bot
```

**Option B: Download ZIP**
1. Go to the repository page on GitHub
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file
5. Open a terminal/command prompt in the extracted folder

### Step 3: Install Python Dependencies

**IMPORTANT for Linux Users:** Modern Linux distributions (Debian 12+, Ubuntu 23.04+) require using a virtual environment. If you get an "externally-managed-environment" error, see the instructions below.

#### Option 1: Using Virtual Environment (Recommended for Linux, Good Practice for All)

**Create and activate virtual environment:**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your command prompt.

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**When you're done using the bot, deactivate:**
```bash
deactivate
```

**Next time you want to run the bot:**
```bash
# Activate the virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Then run the bot
python bot.py
```

#### Option 2: System-Wide Installation (Windows/macOS only)

**Windows:**
```bash
pip install -r requirements.txt
```

**macOS:**
```bash
pip3 install -r requirements.txt
```

⚠️ **Linux users:** System-wide installation is blocked by PEP 668 on modern distributions. Use Option 1 (virtual environment) instead.

This will install:
- `discord.py` - Discord API wrapper for Python
- `aiohttp` - Async HTTP client for API requests
- `python-dotenv` - Environment variable management

**Troubleshooting:**
- **"externally-managed-environment" error on Linux:** This is expected on modern Linux systems. Use Option 1 (virtual environment) above.
- If you get "pip not found", try `python -m pip install -r requirements.txt`
- If you get permission errors on older Linux/macOS, add `--user` flag: `pip3 install --user -r requirements.txt`
- If virtual environment creation fails, install python3-venv: `sudo apt install python3-venv python3-full` (Ubuntu/Debian)

### Step 4: Create Your Discord Bot

Follow these detailed steps to create a Discord bot and get your token:

1. **Go to Discord Developer Portal**
   - Visit [discord.com/developers/applications](https://discord.com/developers/applications)
   - Log in with your Discord account

2. **Create a New Application**
   - Click the "New Application" button (top right)
   - Enter a name for your bot (e.g., "Airline Network Optimizer")
   - Click "Create"

3. **Create the Bot User**
   - In the left sidebar, click "Bot"
   - Click "Add Bot" (or "Reset Token" if bot already exists)
   - Click "Yes, do it!" to confirm

4. **Get Your Bot Token**
   - Under the bot's username, click "Reset Token" (or "Copy" if visible)
   - Click "Yes, do it!" to confirm
   - **Click "Copy" to copy your token**
   - ⚠️ **IMPORTANT:** Keep this token secret! Never share it or commit it to Git

5. **Configure Bot Permissions**
   - Scroll down to "Privileged Gateway Intents"
   - Enable the following intents:
     - ✅ **Message Content Intent** (required)
     - ✅ **Server Members Intent** (optional, but recommended)

6. **Invite Bot to Your Server**
   - In the left sidebar, click "OAuth2" → "URL Generator"
   - Under "Scopes", select:
     - ✅ `bot`
     - ✅ `applications.commands`
   - Under "Bot Permissions", select:
     - ✅ `Send Messages`
     - ✅ `Use Slash Commands`
     - ✅ `Read Message History`
   - Copy the generated URL at the bottom
   - Paste it in your browser and select your server
   - Click "Authorize"

### Step 5: Configure the Bot Token

Create a `.env` file in the bot directory (same folder as `bot.py`):

**Windows (Command Prompt):**
```bash
echo DISCORD_TOKEN=your_token_here > .env
```

**Windows (PowerShell):**
```powershell
"DISCORD_TOKEN=your_token_here" | Out-File -FilePath .env -Encoding ASCII
```

**macOS/Linux:**
```bash
echo "DISCORD_TOKEN=your_token_here" > .env
```

Or create it manually:
1. Create a new file named `.env` (note the dot at the start)
2. Open it in a text editor (Notepad, VS Code, nano, etc.)
3. Add this line (replace with your actual token):
   ```
   DISCORD_TOKEN=your_actual_token_here
   ```
   Your token will look something like: `MTE2ODc5...` (a long string of characters)
4. Save the file

**Verify your .env file:**
```bash
# Windows
type .env

# macOS/Linux
cat .env
```

You should see your token (don't share this output with anyone!)

### Step 6: Run the Bot

**If you used a virtual environment in Step 3, activate it first:**

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your prompt.

**Now start the bot:**

**Windows:**
```bash
python bot.py
```

**macOS/Linux:**
```bash
python3 bot.py
```

**Expected Output:**
```
INFO:__main__:Syncing slash commands...
INFO:__main__:Slash commands synced!
INFO:__main__:Bot logged in as AirlineBot#1234 (ID: 1234567890123456789)
INFO:__main__:------
```

**If you see this, congratulations! Your bot is running! 🎉**

**Common Issues:**
- **"DISCORD_TOKEN environment variable not set!"**
  - Make sure your `.env` file exists and contains your token
  - Make sure you're in the correct directory
  - Try restarting your terminal

- **"discord.py not found" or "ModuleNotFoundError"**
  - If using virtual environment: Make sure it's activated (you should see `(venv)` in your prompt)
  - Run the install command again: `pip install -r requirements.txt`
  - Make sure you're using the same Python version (python vs python3)

- **Bot doesn't come online in Discord:**
  - Check that your token is correct (no extra spaces)
  - Verify the bot is invited to your server
  - Check Discord's status page: [discordstatus.com](https://discordstatus.com)

### Step 7: Use the Bot

1. **Open Discord** and go to your server where you invited the bot
2. **Type `/` in any text channel** - you should see the bot's commands appear
3. **Select `/network-run`** from the command list
4. **Enter your parameters:**
   - `hq_code`: Your airline's headquarters IATA code (e.g., `JFK`, `LAX`, `LHR`)
   - `min_openness` (optional): Minimum country openness (0-10, default: 0)
   - `max_distance` (optional): Maximum distance in km (default: 20000)
5. **Press Enter** and wait for the results!

**Note:** The first time you use the command, it might take a few seconds as the bot fetches data from the API.

## Usage Examples

### Basic Usage

**Find the best airports near JFK:**
```
/network-run hq_code:JFK
```
This searches all airports within 20,000 km (basically worldwide) with no openness restrictions.

**Find airports in open countries near London:**
```
/network-run hq_code:LHR min_openness:7 max_distance:3000
```
This finds airports within 3,000 km of London Heathrow in countries with openness level 7 or higher.

**Find short-haul destinations from Dubai:**
```
/network-run hq_code:DXB max_distance:2000
```
This finds airports within 2,000 km of Dubai, perfect for short-haul routes.

### Understanding the Output

When you run the command, the bot will respond with a table like this:

```
Rank | IATA | Name                   | CC(Open) | Dist(km) | Pop     | Income | CompSeats | BOS
-----------------------------------------------------------------------------------------------
   1 | LAX  | Los Angeles Intl       | US(10)   |   3974.2 | 3000000 |     55 |     25000 | 2500000.50
   2 | ORD  | Chicago O'Hare         | US(10)   |   1185.5 | 2500000 |     52 |     30000 | 1950000.25
   3 | ATL  | Atlanta Hartsfield     | US(10)   |   1209.8 | 2800000 |     53 |     35000 | 1875000.75
```

**Column Meanings:**
- **Rank**: Position in the list (1 is best)
- **IATA**: 3-letter airport code
- **Name**: Airport name (shortened if too long)
- **CC(Open)**: Country code with openness level in parentheses (higher is better)
- **Dist(km)**: Distance from your HQ in kilometers
- **Pop**: Airport population (passenger demand indicator)
- **Income**: Income level (affects ticket prices)
- **CompSeats**: Total competition seats from existing airlines
- **BOS**: Base Opportunity Score (higher = better opportunity)

## How It Works

### What is Base Opportunity Score (BOS)?

BOS is a formula that helps you find the best airports to expand your airline network. It considers:
- **Population**: More people = more potential passengers
- **Income**: Higher income = people can afford more expensive tickets
- **Competition**: More competition = harder to make profit
- **Distance**: Sweet spot is 200-2000 km from your HQ

### The BOS Formula (For the Math-Inclined)

```
distance_factor = 0.1 if distance < 200km          (too close = penalty)
                  1.5 if 200km ≤ distance ≤ 2000km (sweet spot = bonus)
                  1.0 if distance > 2000km         (normal long-haul)

competition_score = competition_seats / 10000

BOS = (Population^0.7 × Income^1.3) / (1 + competition_score)^1.5 × distance_factor
```

**What this means:**
- Airports with **high population and income** get higher scores
- Airports with **lots of competition** get lower scores
- Airports **200-2000 km away** get a 1.5x bonus (optimal distance)
- Airports **under 200 km** get a 0.1x penalty (too close to HQ)
- Airports **over 2000 km** are normal (no bonus or penalty)

### How the Bot Works (Behind the Scenes)

When you run `/network-run`, here's what happens:

**Phase 1 - Data Collection (1-2 seconds):**
1. Bot fetches all countries and their openness levels from Airline Club
2. Bot fetches all airports from Airline Club (cached for 10 minutes)
3. Bot finds your HQ airport by IATA code
4. Bot calculates distance from HQ to every airport using the Haversine formula
5. Bot filters out airports that don't meet your criteria

**Phase 2 - Competition Analysis (5-15 seconds):**
1. For each remaining airport, bot fetches existing airline routes
2. Bot counts total seats from all competing airlines
3. Bot can check up to 20 airports simultaneously for speed

**Phase 3 - Scoring & Results (< 1 second):**
1. Bot calculates BOS for each airport
2. Bot sorts airports by BOS (highest to lowest)
3. Bot takes the top 15 airports
4. Bot formats a nice table and sends it to Discord

**Total time:** Usually 7-20 seconds depending on how many airports pass your filters.

## Project Structure

```
.
├── bot.py                 # Main entrypoint - starts the Discord bot
├── cogs/
│   ├── __init__.py
│   └── network.py         # /network-run command implementation
├── utils/
│   ├── __init__.py
│   ├── http.py            # HTTP client with caching
│   ├── geo.py             # Haversine distance calculation
│   └── scoring.py         # BOS calculation logic
├── requirements.txt       # Python dependencies
├── .env                   # Your Discord token (create this!)
├── .env.example           # Example configuration file
├── .gitignore
├── LICENSE
└── README.md
```

## Advanced Setup (Optional)

### Using a Virtual Environment

It's a good practice to use a virtual environment to isolate dependencies:

**Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies in the virtual environment:**
```bash
pip install -r requirements.txt
```

**Deactivate when done:**
```bash
deactivate
```

### Running as a Background Service

**Linux (systemd):**

Create a service file `/etc/systemd/system/airline-bot.service`:
```ini
[Unit]
Description=Airline Network Optimizer Discord Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/ac-connection-comparison-discord-bot
Environment="DISCORD_TOKEN=your_token_here"
ExecStart=/usr/bin/python3 /path/to/ac-connection-comparison-discord-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable airline-bot
sudo systemctl start airline-bot
sudo systemctl status airline-bot
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup")
4. Action: Start a program
5. Program: `python` or `pythonw` (for no console)
6. Arguments: `bot.py`
7. Start in: `C:\path\to\bot\directory`

**Using screen/tmux (Linux/macOS):**
```bash
screen -S airline-bot
python3 bot.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r airline-bot
```

### Keeping the Bot Updated

To update the bot to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python bot.py
```

## Frequently Asked Questions (FAQ)

### General Questions

**Q: What is Airline Club?**  
A: Airline Club is an online airline management simulation game where you manage your own airline. This bot helps you decide which airports to add to your network.

**Q: Do I need to play Airline Club to use this bot?**  
A: The bot is designed for Airline Club players, but you can use it to explore real-world airport data.

**Q: Is this bot official or affiliated with Airline Club?**  
A: No, this is a community-created tool that uses Airline Club's public API.

**Q: Does the bot cost money?**  
A: No, the bot is completely free and open-source.

### Setup Questions

**Q: I've never coded before. Can I still set this up?**  
A: Yes! This guide is written for beginners. Just follow the steps carefully. If you get stuck, check the Troubleshooting section.

**Q: Do I need to keep my computer running for the bot to work?**  
A: Yes, the bot only runs while your computer is on and the program is running. See "Advanced Setup" for running it as a background service.

**Q: Can I host this on a server or Raspberry Pi?**  
A: Yes! The bot works on any system that can run Python 3.9+. See the "Advanced Setup" section for Linux service setup.

**Q: What is a ".env" file and why can't I see it?**  
A: The `.env` file stores your Discord token. Files starting with a dot are hidden by default. On Windows, enable "Show hidden files" in File Explorer. On macOS/Linux, use `ls -la` to see it.

**Q: I'm getting "externally-managed-environment" error on Linux. What do I do?**  
A: This is normal on modern Linux systems (Debian 12+, Ubuntu 23.04+). You must use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
See Step 3 in the setup guide for detailed instructions. This is now standard practice on Linux to prevent breaking system packages.

### Usage Questions

**Q: What's a good `min_openness` value?**  
A: 
- `0-3`: Very restricted countries (difficult to operate)
- `4-6`: Moderate restrictions
- `7-10`: Open countries (easiest to operate)
- Recommendation: Start with `min_openness:5` for a good balance

**Q: What's a good `max_distance` value?**  
A:
- `0-1000 km`: Very short regional routes
- `1000-3000 km`: Short to medium routes (good profit potential)
- `3000-6000 km`: Medium to long routes
- `6000+ km`: Long-haul international routes
- Recommendation: Try `max_distance:3000` for profitable routes

**Q: Why are there only 15 results?**  
A: The bot limits results to 15 to keep the message short and show only the best opportunities. The top 15 are usually the most valuable airports anyway.

**Q: Can I search for airports without specifying a HQ?**  
A: No, the HQ is required because the bot needs to calculate distances and the distance factor affects the BOS score.

**Q: What does "CompSeats" mean?**  
A: CompSeats (Competition Seats) is the total number of seats offered by all other airlines flying to that airport. Higher competition means it's harder to make profit there.

**Q: Why does the bot take 10-20 seconds to respond?**  
A: The bot needs to:
1. Fetch data for thousands of airports
2. Calculate distances for hundreds of airports
3. Check competition for up to 20 airports
This is normal! The bot caches data to make subsequent searches faster.

### Technical Questions

**Q: What is "caching" and why is it important?**  
A: Caching means the bot saves airport data for 10 minutes so it doesn't have to re-download it every time. This makes the bot faster and reduces load on the Airline Club servers.

**Q: Can I change the cache time?**  
A: Yes, edit `CACHE_TTL` in `utils/http.py` (value is in seconds: 600 = 10 minutes).

**Q: Can I run multiple bots with the same code?**  
A: Yes, but each bot needs its own Discord token and should be a separate application in the Discord Developer Portal.

**Q: The bot says "Syncing slash commands" but they don't appear. What do I do?**  
A: Discord can take up to 5 minutes to register commands globally. During development, you can test faster by registering commands to a specific guild/server - see Discord.py documentation for details.

**Q: Can I customize the output format?**  
A: Yes, edit the `_format_table` method in `cogs/network.py`. You can change column widths, order, or what data is displayed.

**Q: Can I add more commands to the bot?**  
A: Yes! Create new commands in `cogs/network.py` or create a new cog file in the `cogs/` directory.

### Troubleshooting Questions

**Q: I get "Module not found" errors. What should I do?**  
A: Run `pip install -r requirements.txt` again. Make sure you're using the same Python command for installing and running (e.g., both `python3` or both `python`).

**Q: The bot starts but doesn't respond to commands. Help!**  
A:
1. Wait 1-5 minutes for Discord to sync commands
2. Check that the bot has "Use Application Commands" permission
3. Try typing `/` in Discord to refresh the command list
4. Check console output for errors
5. Try removing and re-inviting the bot

**Q: I accidentally shared my token! What do I do?**  
A: 
1. Go to Discord Developer Portal immediately
2. Reset your bot token
3. Update your `.env` file with the new token
4. Restart the bot
Never share your token or `.env` file with anyone!

**Q: Can I see the bot's code?**  
A: Yes! All the code is in this repository. The main files are `bot.py` and `cogs/network.py`.

## Troubleshooting

### Installation Issues

**"externally-managed-environment" error on Linux:**
- **This is the most common issue on modern Linux systems (Debian 12+, Ubuntu 23.04+)**
- Modern Linux distributions implement PEP 668 to prevent breaking system packages
- **Solution:** Use a virtual environment (recommended):
  ```bash
  # Create virtual environment
  python3 -m venv venv
  
  # Activate it
  source venv/bin/activate
  
  # Install dependencies
  pip install -r requirements.txt
  
  # Run the bot (virtual environment must be activated)
  python bot.py
  ```
- If `python3 -m venv` fails, install venv support: `sudo apt install python3-venv python3-full`
- Alternative (not recommended): Use `--break-system-packages` flag, but this can cause system issues

**"Python not found" or "pip not found":**
- Make sure Python is installed and added to PATH
- Try using `python3` and `pip3` instead of `python` and `pip`
- On Windows, try `py -3` instead of `python`

**"Permission denied" when installing packages:**
- On modern Linux: Use virtual environment (see above)
- On older Linux/macOS: `pip3 install --user -r requirements.txt`

**"Module not found" errors when running the bot:**
- If using virtual environment: Make sure it's activated (you should see `(venv)` in prompt)
- Make sure you installed dependencies: `pip install -r requirements.txt`
- Check you're using the same Python version for both installing and running
- Try: `python -m pip install -r requirements.txt` then `python bot.py`

### Bot Configuration Issues

**"DISCORD_TOKEN environment variable not set!":**
- Make sure your `.env` file exists in the same directory as `bot.py`
- Open `.env` and verify your token is there (one line: `DISCORD_TOKEN=your_token`)
- No quotes needed around the token
- No spaces before or after the `=` sign

**Bot doesn't appear online in Discord:**
- Verify your token is correct (try resetting it in Discord Developer Portal)
- Make sure you invited the bot to your server
- Check that the bot has "Presence Intent" enabled (optional but helpful)
- Wait a minute - sometimes Discord takes time to update

**Slash commands don't appear:**
- Wait 1-5 minutes after starting the bot (Discord needs time to register commands)
- Try typing `/` in Discord to refresh the command list
- Make sure the bot has "Use Application Commands" permission
- Check console output - you should see "Slash commands synced!"
- If still not working, kick and re-invite the bot to your server

### Runtime Issues

**"Failed to fetch data from Airline Club API":**
- Check your internet connection
- The Airline Club website might be down - try visiting [airline-club.com](https://www.airline-club.com) in your browser
- The API might be rate-limiting - wait a minute and try again
- Check the bot console for more detailed error messages

**"Airport with IATA code 'XXX' not found":**
- Make sure you're using a valid 3-letter IATA code
- IATA codes are case-insensitive (jfk, JFK, Jfk all work)
- Some small airports might not be in the Airline Club database
- Try a major airport like JFK, LAX, LHR, or DXB to test

**Bot crashes or stops responding:**
- Check the console for error messages
- Try restarting the bot: press Ctrl+C, then run `python bot.py` again
- Make sure you have a stable internet connection
- Check if you're hitting API rate limits (bot caches data for 10 minutes to help with this)

**"No airports found matching the criteria":**
- Try increasing `max_distance` (default is 20000 km)
- Try lowering `min_openness` (default is 0)
- Make sure your HQ airport code is correct

### Getting Help

If you're still having issues:

1. **Check the console output** - error messages often explain the problem
2. **Verify your setup:**
   ```bash
   python --version  # Should be 3.9+
   pip show discord.py  # Should show version 2.0+
   cat .env  # Should show your token (don't share this!)
   ```
3. **Try with a fresh token** - reset your bot token in Discord Developer Portal
4. **Create an issue** on the GitHub repository with:
   - Your Python version
   - Console error messages (remove your token if present)
   - Steps to reproduce the problem

## For Developers

### Architecture Overview

This bot uses a modular architecture with clear separation of concerns:

- **Modular Design**: Separate utilities for HTTP, geography, and scoring
- **Async/Await**: Fully asynchronous using aiohttp and discord.py
- **Type Hints**: Type annotations throughout for better IDE support
- **Graceful Error Handling**: Timeout handling, API failures, and user errors
- **Rate Limiting**: Semaphore-based concurrency control (max 20 concurrent requests)
- **Caching**: In-memory TTL cache to reduce API load

### Code Structure

**bot.py**: Main entrypoint
- Initializes Discord client
- Configures logging
- Loads cogs (command modules)
- Manages HTTP client lifecycle

**cogs/network.py**: Command implementation
- `/network-run` slash command
- Three-phase execution (fetch, analyze, score)
- Table formatting
- Error handling and user feedback

**utils/http.py**: HTTP client
- aiohttp ClientSession wrapper
- TTL caching system
- Timeout configuration
- Error logging

**utils/geo.py**: Geographic calculations
- Haversine distance formula
- Earth radius: 6371 km

**utils/scoring.py**: Scoring logic
- BOS formula implementation
- Distance factor calculation
- Competition penalty

### Testing the Bot

Manual testing:
1. Create a test Discord server
2. Invite the bot to your test server
3. Run the bot with `python bot.py`
4. Test with various parameters:
   ```
   /network-run hq_code:JFK
   /network-run hq_code:LAX min_openness:8 max_distance:5000
   /network-run hq_code:INVALID (test error handling)
   ```

### Contributing

Contributions are welcome! Here's how to contribute:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear commit messages
4. **Test thoroughly** - make sure the bot still works
5. **Submit a pull request** with a description of your changes

**Code style:**
- Follow PEP 8 Python style guidelines
- Use type hints
- Add docstrings to functions
- Use async/await properly
- Log errors appropriately

**Ideas for contributions:**
- Add more slash commands (e.g., route profitability calculator)
- Improve error messages
- Add data visualization (charts, graphs)
- Support for multiple languages
- Add unit tests
- Performance optimizations
- Database support for persistent caching

## License

This bot is provided under the MIT License. See LICENSE file for details.

This bot is provided as-is for use with Airline Club game. Not affiliated with or endorsed by Airline Club.

## Credits

Data provided by [Airline Club](https://www.airline-club.com)
