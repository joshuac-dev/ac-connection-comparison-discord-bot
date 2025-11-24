"""HTTP utility functions for API requests with caching."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
import aiohttp


# Set up logging
logger = logging.getLogger(__name__)

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
            self.session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers=HEADERS
            )
    
    async def close(self):
        """Close the HTTP client session."""
        if self.session:
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
            if time.time() - cached["timestamp"] < CACHE_TTL:
                return cached["data"]
        
        # Make request
        url = f"{BASE_URL}{endpoint}"
        try:
            if self.session is None:
                await self.start()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache the result
                    if use_cache:
                        _cache[cache_key] = {
                            "data": data,
                            "timestamp": time.time(),
                        }
                    
                    return data
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def fetch_countries(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch list of countries.
        
        Returns:
            List of country objects or None if request fails
        """
        return await self.fetch_json("/api/countries", use_cache=True)
    
    async def fetch_airports(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch list of airports.
        
        Returns:
            List of airport objects or None if request fails
        """
        return await self.fetch_json("/api/airports", use_cache=True)
    
    async def fetch_airport_links(self, airport_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch links for a specific airport.
        
        Args:
            airport_id: Airport ID
        
        Returns:
            List of link objects or None if request fails
        """
        return await self.fetch_json(
            f"/api/airport/{airport_id}/links",
            use_cache=False,  # Don't cache individual airport links
        )


# Global HTTP client instance
http_client = HTTPClient()
