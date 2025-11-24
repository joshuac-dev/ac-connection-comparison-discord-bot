"""Network optimization cog for the Discord bot."""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Tuple
import discord
from discord import app_commands
from discord.ext import commands

from utils.http import http_client
from utils.geo import haversine_distance
from utils.scoring import calculate_bos


# Set up logging
logger = logging.getLogger(__name__)

# Check DEBUG mode
DEBUG_MODE = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")


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
        
        logger.debug(f"========== NETWORK-RUN COMMAND STARTED ==========")
        logger.debug(f"Parameters: hq_code={hq_code}, min_openness={min_openness}, max_distance={max_distance}")
        logger.debug(f"User: {interaction.user} (ID: {interaction.user.id})")
        logger.debug(f"Guild: {interaction.guild.name if interaction.guild else 'DM'}")
        
        try:
            # Phase A: Fetch data and filter airports
            hq_code = hq_code.upper()
            logger.debug(f"PHASE A: Fetching data for HQ code: {hq_code}")
            
            # Fetch countries and airports concurrently
            logger.debug("Fetching countries and airports from API...")
            countries_data, airports_data = await asyncio.gather(
                http_client.fetch_countries(),
                http_client.fetch_airports(),
            )
            
            if countries_data is None or airports_data is None:
                logger.error("Failed to fetch data from Airline Club API")
                logger.debug(f"countries_data is None: {countries_data is None}")
                logger.debug(f"airports_data is None: {airports_data is None}")
                await interaction.followup.send(
                    "❌ Failed to fetch data from Airline Club API. Please try again later.",
                    ephemeral=True,
                )
                return
            
            logger.debug(f"Fetched {len(countries_data)} countries")
            logger.debug(f"Fetched {len(airports_data)} airports")
            
            # Sample first country data for debugging
            if DEBUG_MODE and countries_data:
                logger.debug(f"Sample country data: {countries_data[0]}")
            
            # Sample first airport data for debugging
            if DEBUG_MODE and airports_data:
                logger.debug(f"Sample airport data: {airports_data[0]}")
            
            # Build country openness map
            country_openness: Dict[str, int] = {}
            for country in countries_data:
                code = country.get("countryCode", "")
                openness_val = country.get("openness", 0)
                country_openness[code] = openness_val
            
            logger.debug(f"Built openness map for {len(country_openness)} countries")
            
            # Find HQ airport
            hq_airport = None
            for airport in airports_data:
                if airport.get("iata", "").upper() == hq_code:
                    hq_airport = airport
                    break
            
            if hq_airport is None:
                logger.warning(f"HQ airport '{hq_code}' not found in data")
                await interaction.followup.send(
                    f"❌ Airport with IATA code '{hq_code}' not found.",
                    ephemeral=True,
                )
                return
            
            hq_lat = hq_airport.get("latitude", 0)
            hq_lon = hq_airport.get("longitude", 0)
            hq_id = hq_airport.get("id")
            
            logger.debug(f"Found HQ airport: {hq_airport.get('name', 'Unknown')}")
            logger.debug(f"HQ ID: {hq_id}, Lat: {hq_lat}, Lon: {hq_lon}")
            logger.debug(f"HQ airport full data: {hq_airport}")
            
            # Filter airports
            logger.debug(f"PHASE A: Filtering airports (openness >= {min_openness}, distance <= {max_distance} km)")
            filtered_airports = []
            skipped_hq = 0
            skipped_openness = 0
            skipped_distance = 0
            
            for airport in airports_data:
                # Skip HQ itself
                if airport.get("id") == hq_id:
                    skipped_hq += 1
                    continue
                
                # Check openness
                country_code = airport.get("countryCode", "")
                openness = country_openness.get(country_code, 0)
                if openness < min_openness:
                    skipped_openness += 1
                    continue
                
                # Check distance
                lat = airport.get("latitude", 0)
                lon = airport.get("longitude", 0)
                distance = haversine_distance(hq_lat, hq_lon, lat, lon)
                if distance > max_distance:
                    skipped_distance += 1
                    continue
                
                # Add airport with computed distance and openness
                filtered_airports.append({
                    "airport": airport,
                    "distance": distance,
                    "openness": openness,
                })
            
            logger.debug(f"Filter results:")
            logger.debug(f"  - Skipped (HQ itself): {skipped_hq}")
            logger.debug(f"  - Skipped (openness < {min_openness}): {skipped_openness}")
            logger.debug(f"  - Skipped (distance > {max_distance}): {skipped_distance}")
            logger.debug(f"  - Passed filter: {len(filtered_airports)} airports")
            
            if not filtered_airports:
                logger.warning("No airports passed the filter criteria")
                await interaction.followup.send(
                    f"No airports found matching the criteria (openness >= {min_openness}, distance <= {max_distance} km).",
                    ephemeral=True,
                )
                return
            
            # Phase B: Fetch competition data concurrently
            logger.debug(f"PHASE B: Fetching competition data for {len(filtered_airports)} airports")
            
            async def fetch_competition(airport_data: Dict) -> Dict:
                """Fetch competition for a single airport."""
                airport = airport_data["airport"]
                airport_id = airport.get("id")
                airport_iata = airport.get("iata", "???")
                
                async with self.semaphore:
                    logger.debug(f"Fetching links for airport {airport_iata} (ID: {airport_id})")
                    links = await http_client.fetch_airport_links(airport_id)
                    
                    if links is None:
                        logger.debug(f"  -> Links fetch returned None for {airport_iata}")
                        competition = 0
                    elif isinstance(links, list):
                        logger.debug(f"  -> Got list of {len(links)} links for {airport_iata}")
                        if links and DEBUG_MODE:
                            # Log the first link structure to understand the data
                            first_link = links[0] if links else None
                            if first_link:
                                logger.debug(f"  -> First link structure: {first_link}")
                                logger.debug(f"  -> First link keys: {first_link.keys() if isinstance(first_link, dict) else 'not a dict'}")
                        competition = 0
                        for link in links:
                            if isinstance(link, dict):
                                # Try multiple possible key names for capacity
                                cap = link.get("capacity", link.get("assignedCapacity", link.get("totalCapacity", 0)))
                                if isinstance(cap, dict):
                                    # Capacity might be nested, try to extract a total
                                    cap = cap.get("total", cap.get("economy", 0)) + cap.get("business", 0) + cap.get("first", 0)
                                if isinstance(cap, (int, float)):
                                    competition += cap
                                else:
                                    logger.debug(f"  -> Non-numeric capacity in link: {type(cap)} = {cap}")
                        logger.debug(f"  -> Total competition for {airport_iata}: {competition}")
                    elif isinstance(links, dict):
                        logger.debug(f"  -> Got dict response for {airport_iata}, keys: {list(links.keys())}")
                        if DEBUG_MODE:
                            logger.debug(f"  -> Dict content sample: {str(links)[:500]}")
                        link_list = links.get("links", links.get("data", []))
                        competition = 0
                        if isinstance(link_list, list):
                            logger.debug(f"  -> Extracted {len(link_list)} links from dict")
                            if link_list and DEBUG_MODE:
                                logger.debug(f"  -> First link from dict: {link_list[0]}")
                            for link in link_list:
                                if isinstance(link, dict):
                                    cap = link.get("capacity", link.get("assignedCapacity", link.get("totalCapacity", 0)))
                                    if isinstance(cap, dict):
                                        cap = cap.get("total", cap.get("economy", 0)) + cap.get("business", 0) + cap.get("first", 0)
                                    if isinstance(cap, (int, float)):
                                        competition += cap
                        logger.debug(f"  -> Total competition for {airport_iata}: {competition}")
                    else:
                        logger.debug(f"  -> Unexpected links type for {airport_iata}: {type(links)}")
                        competition = 0
                    
                    airport_data["competition"] = competition
                    return airport_data
            
            # Fetch all competition data concurrently
            results = await asyncio.gather(
                *[fetch_competition(data) for data in filtered_airports]
            )
            
            logger.debug(f"PHASE B: Completed fetching competition for {len(results)} airports")
            
            # Summary of competition data
            airports_with_competition = sum(1 for r in results if r.get("competition", 0) > 0)
            airports_no_competition = len(results) - airports_with_competition
            total_competition = sum(r.get("competition", 0) for r in results)
            logger.debug(f"Competition summary:")
            logger.debug(f"  - Airports with competition > 0: {airports_with_competition}")
            logger.debug(f"  - Airports with 0 competition: {airports_no_competition}")
            logger.debug(f"  - Total competition seats: {total_competition}")
            
            # Phase C: Calculate BOS and prepare results
            logger.debug("PHASE C: Calculating BOS scores")
            scored_airports = []
            skipped_zero_pop = 0
            skipped_zero_income = 0
            skipped_bos_none = 0
            
            for data in results:
                airport = data["airport"]
                distance = data["distance"]
                openness = data["openness"]
                competition = data["competition"]
                
                population = airport.get("population", 0)
                income_level = airport.get("incomeLevel", 0)
                
                logger.debug(f"Scoring {airport.get('iata', '???')}: pop={population}, income={income_level}, comp={competition}, dist={distance:.1f}")
                
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
                    logger.debug(f"  -> BOS = {bos:.2f}")
                else:
                    if population <= 0:
                        skipped_zero_pop += 1
                    elif income_level <= 0:
                        skipped_zero_income += 1
                    else:
                        skipped_bos_none += 1
                    logger.debug(f"  -> Skipped (BOS=None)")
            
            logger.debug(f"Scoring results:")
            logger.debug(f"  - Valid scores: {len(scored_airports)}")
            logger.debug(f"  - Skipped (zero population): {skipped_zero_pop}")
            logger.debug(f"  - Skipped (zero income): {skipped_zero_income}")
            logger.debug(f"  - Skipped (BOS calculation failed): {skipped_bos_none}")
            
            if not scored_airports:
                logger.warning("No airports with valid BOS scores")
                await interaction.followup.send(
                    "No valid airports found after scoring (need positive population and income).",
                    ephemeral=True,
                )
                return
            
            # Sort by BOS descending and take top 15
            scored_airports.sort(key=lambda x: x["bos"], reverse=True)
            top_airports = scored_airports[:15]
            
            logger.debug(f"Top 15 airports by BOS:")
            for i, ap in enumerate(top_airports, 1):
                logger.debug(f"  {i}. {ap['iata']}: BOS={ap['bos']:.2f}, pop={ap['population']}, income={ap['income']}, comp={ap['competition']}")
            
            # Format output table
            table = self._format_table(top_airports)
            
            logger.debug(f"========== NETWORK-RUN COMMAND COMPLETED ==========")
            logger.debug(f"Returning {len(top_airports)} results to user")
            
            # Send response
            await interaction.followup.send(f"```\n{table}\n```")
            
        except Exception as e:
            logger.error(f"Error in network-run command: {e}")
            logger.exception("Full exception traceback:")
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
