"""Network optimization cog for the Discord bot."""

import asyncio
from typing import Dict, List, Optional, Tuple
import discord
from discord import app_commands
from discord.ext import commands

from utils.http import http_client
from utils.geo import haversine_distance
from utils.scoring import calculate_bos


class NetworkCog(commands.Cog):
    """Cog for network optimization commands."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the network cog."""
        self.bot = bot
        # Semaphore for bounded concurrency
        self.semaphore = asyncio.Semaphore(20)
    
    @app_commands.command(
        name="network-run",
        description="Find optimal airports for your airline network"
    )
    @app_commands.describe(
        hq_code="IATA code of your headquarters airport (e.g., LAX, JFK)",
        min_openness="Minimum country openness (0-10, default: 0)",
        max_distance="Maximum distance from HQ in km (default: 20000)"
    )
    async def network_run(
        self,
        interaction: discord.Interaction,
        hq_code: str,
        min_openness: Optional[int] = 0,
        max_distance: Optional[int] = 20000,
    ):
        """
        Find optimal airports for airline network based on HQ location.
        
        Args:
            interaction: Discord interaction
            hq_code: IATA code of HQ airport
            min_openness: Minimum country openness filter
            max_distance: Maximum distance from HQ filter
        """
        # Defer response as this will take time
        await interaction.response.defer()
        
        try:
            # Phase A: Fetch data and filter airports
            hq_code = hq_code.upper()
            
            # Fetch countries and airports concurrently
            countries_data, airports_data = await asyncio.gather(
                http_client.fetch_countries(),
                http_client.fetch_airports(),
            )
            
            if countries_data is None or airports_data is None:
                await interaction.followup.send(
                    "❌ Failed to fetch data from Airline Club API. Please try again later.",
                    ephemeral=True,
                )
                return
            
            # Build country openness map
            country_openness: Dict[str, int] = {
                country["countryCode"]: country.get("openness", 0)
                for country in countries_data
            }
            
            # Find HQ airport
            hq_airport = None
            for airport in airports_data:
                if airport.get("iata", "").upper() == hq_code:
                    hq_airport = airport
                    break
            
            if hq_airport is None:
                await interaction.followup.send(
                    f"❌ Airport with IATA code '{hq_code}' not found.",
                    ephemeral=True,
                )
                return
            
            hq_lat = hq_airport.get("latitude", 0)
            hq_lon = hq_airport.get("longitude", 0)
            hq_id = hq_airport.get("id")
            
            # Filter airports
            filtered_airports = []
            for airport in airports_data:
                # Skip HQ itself
                if airport.get("id") == hq_id:
                    continue
                
                # Check openness
                country_code = airport.get("countryCode", "")
                openness = country_openness.get(country_code, 0)
                if openness < min_openness:
                    continue
                
                # Check distance
                lat = airport.get("latitude", 0)
                lon = airport.get("longitude", 0)
                distance = haversine_distance(hq_lat, hq_lon, lat, lon)
                if distance > max_distance:
                    continue
                
                # Add airport with computed distance and openness
                filtered_airports.append({
                    "airport": airport,
                    "distance": distance,
                    "openness": openness,
                })
            
            if not filtered_airports:
                await interaction.followup.send(
                    f"No airports found matching the criteria (openness >= {min_openness}, distance <= {max_distance} km).",
                    ephemeral=True,
                )
                return
            
            # Phase B: Fetch competition data concurrently
            async def fetch_competition(airport_data: Dict) -> Dict:
                """Fetch competition for a single airport."""
                airport = airport_data["airport"]
                airport_id = airport.get("id")
                
                async with self.semaphore:
                    links = await http_client.fetch_airport_links(airport_id)
                    
                    if links is None:
                        # Treat as 0 competition if fetch fails
                        competition = 0
                    else:
                        # Sum capacities
                        competition = sum(
                            link.get("capacity", 0) for link in links
                        )
                    
                    airport_data["competition"] = competition
                    return airport_data
            
            # Fetch all competition data concurrently
            results = await asyncio.gather(
                *[fetch_competition(data) for data in filtered_airports]
            )
            
            # Phase C: Calculate BOS and prepare results
            scored_airports = []
            for data in results:
                airport = data["airport"]
                distance = data["distance"]
                openness = data["openness"]
                competition = data["competition"]
                
                population = airport.get("population", 0)
                income_level = airport.get("incomeLevel", 0)
                
                bos = calculate_bos(population, income_level, competition, distance)
                
                if bos is not None:
                    scored_airports.append({
                        "iata": airport.get("iata", "???"),
                        "name": airport.get("name", "Unknown"),
                        "country_code": airport.get("countryCode", "??"),
                        "openness": openness,
                        "distance": distance,
                        "population": population,
                        "income": income_level,
                        "competition": competition,
                        "bos": bos,
                    })
            
            if not scored_airports:
                await interaction.followup.send(
                    "No valid airports found after scoring (need positive population and income).",
                    ephemeral=True,
                )
                return
            
            # Sort by BOS descending and take top 15
            scored_airports.sort(key=lambda x: x["bos"], reverse=True)
            top_airports = scored_airports[:15]
            
            # Format output table
            table = self._format_table(top_airports)
            
            # Send response
            await interaction.followup.send(f"```\n{table}\n```")
            
        except Exception as e:
            print(f"Error in network-run command: {e}")
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True,
            )
    
    def _format_table(self, airports: List[Dict]) -> str:
        """
        Format airports data as a fixed-width table.
        
        Args:
            airports: List of airport data dictionaries
        
        Returns:
            Formatted table string
        """
        # Build header
        lines = []
        header = (
            "Rank | IATA | Name                   | CC(Open) | Dist(km) | "
            "Pop     | Income | CompSeats | BOS"
        )
        separator = "-" * len(header)
        lines.append(header)
        lines.append(separator)
        
        # Build rows
        for i, airport in enumerate(airports, 1):
            # Truncate name to 22 characters
            name = airport["name"][:22].ljust(22)
            
            row = (
                f"{i:4d} | "
                f"{airport['iata']:4s} | "
                f"{name} | "
                f"{airport['country_code']:2s}({airport['openness']:2d})   | "
                f"{airport['distance']:8.1f} | "
                f"{airport['population']:7d} | "
                f"{airport['income']:6d} | "
                f"{airport['competition']:9d} | "
                f"{airport['bos']:6.2f}"
            )
            lines.append(row)
        
        table = "\n".join(lines)
        
        # Ensure table fits within Discord message limit (2000 chars)
        if len(table) > 1900:
            # Truncate if too long (shouldn't happen with 15 entries)
            table = table[:1900] + "..."
        
        return table


async def setup(bot: commands.Bot):
    """Set up the network cog."""
    await bot.add_cog(NetworkCog(bot))
