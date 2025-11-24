"""HTTP utility functions for API requests with caching."""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional
import aiohttp


# Set up logging
logger = logging.getLogger(__name__)

# Check DEBUG mode
DEBUG_MODE = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

# HTTP headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    # Cookie can be injected here if needed
}

# Base URL for API
BASE_URL = "https://www.airline-club.com"

# Cache TTL in seconds (10 minutes)
CACHE_TTL = 600

# Cache storage
_cache: Dict[str, Dict[str, Any]] = {}


class HTTPClient:
    """HTTP client with caching support."""
    
    def __init__(self):
        """Initialize the HTTP client."""
        self.session: Optional[aiohttp.ClientSession] = None
        self._timeout = aiohttp.ClientTimeout(total=30)
    
    async def start(self):
        """Start the HTTP client session."""
        if self.session is None:
            logger.debug(f"Starting HTTP client session with timeout={self._timeout.total}s")
            logger.debug(f"Base URL: {BASE_URL}")
            logger.debug(f"Headers: {HEADERS}")
            self.session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers=HEADERS
            )
    
    async def close(self):
        """Close the HTTP client session."""
        if self.session:
            logger.debug("Closing HTTP client session")
            await self.session.close()
            self.session = None
    
    async def fetch_json(
        self,
        endpoint: str,
        use_cache: bool = True,
        cache_key: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Fetch JSON data from an endpoint.
        
        Args:
            endpoint: API endpoint (will be appended to BASE_URL)
            use_cache: Whether to use caching
            cache_key: Custom cache key (defaults to endpoint)
        
        Returns:
            JSON response data or None if request fails
        """
        if cache_key is None:
            cache_key = endpoint
        
        # Check cache
        if use_cache and cache_key in _cache:
            cached = _cache[cache_key]
            cache_age = time.time() - cached["timestamp"]
            if cache_age < CACHE_TTL:
                logger.debug(f"Cache HIT for {endpoint} (age: {cache_age:.1f}s)")
                return cached["data"]
            else:
                logger.debug(f"Cache EXPIRED for {endpoint} (age: {cache_age:.1f}s > TTL {CACHE_TTL}s)")
        else:
            logger.debug(f"Cache MISS for {endpoint}")
        
        # Make request
        url = f"{BASE_URL}{endpoint}"
        logger.debug(f"Fetching: {url}")
        
        try:
            if self.session is None:
                await self.start()
            
            start_time = time.time()
            async with self.session.get(url) as response:
                elapsed = time.time() - start_time
                logger.debug(f"Response: HTTP {response.status} in {elapsed:.3f}s")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Log response structure
                    if isinstance(data, list):
                        logger.debug(f"Response data: list with {len(data)} items")
                        if data and DEBUG_MODE:
                            logger.debug(f"First item type: {type(data[0])}")
                            if isinstance(data[0], dict):
                                logger.debug(f"First item keys: {list(data[0].keys())[:10]}")
                    elif isinstance(data, dict):
                        logger.debug(f"Response data: dict with keys: {list(data.keys())[:10]}")
                    else:
                        logger.debug(f"Response data type: {type(data)}")
                    
                    # Cache the result
                    if use_cache:
                        _cache[cache_key] = {
                            "data": data,
                            "timestamp": time.time(),
                        }
                        logger.debug(f"Cached response for {endpoint}")
                    
                    return data
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    response_text = await response.text()
                    logger.debug(f"Error response body: {response_text[:500]}")
                    return None
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            logger.debug(f"Exception type: {type(e).__name__}")
            return None
    
    async def fetch_countries(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch list of countries.
        
        Returns:
            List of country objects or None if request fails
        """
        logger.debug("Fetching countries...")
        result = await self.fetch_json("/countries", use_cache=True)
        if result:
            logger.debug(f"Fetched {len(result) if isinstance(result, list) else 'unknown'} countries")
        return result
    
    async def fetch_airports(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch list of airports.
        
        Returns:
            List of airport objects or None if request fails
        """
        logger.debug("Fetching airports...")
        result = await self.fetch_json("/airports", use_cache=True)
        if result:
            logger.debug(f"Fetched {len(result) if isinstance(result, list) else 'unknown'} airports")
        return result
    
    async def fetch_airport_links(self, airport_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch links for a specific airport.
        
        Args:
            airport_id: Airport ID
        
        Returns:
            List of link objects or None if request fails
        """
        logger.debug(f"Fetching links for airport ID: {airport_id}")
        return await self.fetch_json(
            f"/airports/{airport_id}/links",
            use_cache=False,  # Don't cache individual airport links
        )


# Global HTTP client instance
http_client = HTTPClient()
