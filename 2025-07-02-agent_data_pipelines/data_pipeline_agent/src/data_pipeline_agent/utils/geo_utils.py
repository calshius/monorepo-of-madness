import asyncio
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

async def lookup_lat_lon(town, area, max_retries=3, delay=5):
    """
    Async lookup for latitude and longitude for a given town and area.
    Retries on failure and throttles requests to avoid rate limits.
    Returns (latitude, longitude) as strings, or ("NA", "NA") if not found.
    """
    for attempt in range(1, max_retries + 1):
        try:
            async with Nominatim(
                user_agent="ufo_map_agent",
                adapter_factory=AioHTTPAdapter,
            ) as geolocator:
                # Try town + area
                if (
                    town
                    and area
                    and "nothing" not in town.lower()
                    and "nothing" not in area.lower()
                ):
                    query = f"{town}, {area}"
                    location = await geolocator.geocode(
                        query, timeout=10, country_codes=["gb"]
                    )
                    print(f"Query: {query} -> {location}")
                    if location:
                        await asyncio.sleep(delay)
                        return str(location.latitude), str(location.longitude)
                # Try just town
                if town and "nothing" not in town.lower():
                    query = town
                    location = await geolocator.geocode(
                        query, timeout=10, country_codes=["gb"]
                    )
                    print(f"Query: {query} -> {location}")
                    if location:
                        await asyncio.sleep(delay)
                        return str(location.latitude), str(location.longitude)
                # Try just area
                if area and "nothing" not in area.lower():
                    query = area
                    location = await geolocator.geocode(
                        query, timeout=10, country_codes=["gb"]
                    )
                    print(f"Query: {query} -> {location}")
                    if location:
                        await asyncio.sleep(delay)
                        return str(location.latitude), str(location.longitude)
        except Exception as e:
            print(f"Geocode error for town='{town}', area='{area}' (attempt {attempt}): {e}")
            await asyncio.sleep(delay * attempt)
    return "NA", "NA"