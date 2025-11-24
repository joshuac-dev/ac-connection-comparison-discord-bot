"""Discord bot entrypoint for Airline Network Optimizer."""

import os
import sys
import asyncio
import logging
import discord
from discord.ext import commands

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.http import http_client


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class AirlineBot(commands.Bot):
    """Custom bot class for airline network optimization."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",  # Prefix for legacy commands (not used)
            intents=intents,
        )
    
    async def setup_hook(self):
        """Set up the bot before it starts."""
        # Start HTTP client
        await http_client.start()
        
        # Load cogs
        await self.load_extension("cogs.network")
        
        # Sync slash commands
        logger.info("Syncing slash commands...")
        await self.tree.sync()
        logger.info("Slash commands synced!")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")
    
    async def close(self):
        """Clean up resources when bot is closing."""
        await http_client.close()
        await super().close()


async def main():
    """Main entrypoint for the bot."""
    # Get Discord token from environment
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        logger.error("Please set DISCORD_TOKEN before running the bot.")
        sys.exit(1)
    
    # Create and run bot
    bot = AirlineBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
