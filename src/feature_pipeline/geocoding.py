from loguru import logger
from geopy import Nominatim, Photon
from collections.abc import AsyncGenerator

from src.setup.config import general_config 
from src.setup.custom_types import FeedData
from src.feature_pipeline.server import poll_feed


async def get_station_geodata(city_name: str, feed_name: str = "station_information") -> AsyncGenerator[FeedData]:
    yield await poll_feed(feed_name=feed_name, city_name=city_name)


def reverse_geocode(latitude: float, longitude: float) -> dict[str, list[float]]: 
    """
    Take a latitude and longitude, and request its address from Nominatim. If that fails,
    a request will be made to Photon. If this second attempt fails, the address will read "None".
    I don't expect that there'll be many of these, but I'll investigate these locations at some 
    point in the future

    Args:
        latitude: the latitude of the coordinate in question. 
        longitude: the longitude of the coordinate in question. 
    """
    geodata: dict[str, list[float]] = {}
    coordinate = [latitude, longitude]

    try:
        nominatim = Nominatim(user_agent=general_config.email)
        first_try = str(nominatim.reverse(query=coordinate))

        if first_try != "None":
            geodata[first_try] = coordinate
        else:
            photon = Photon(user_agent=general_config.email)
            second_try = str(photon.reverse(query=coordinate))  # If this returns "None" (unlikely), we will look into it later.
            geodata[second_try] = coordinate  

        return geodata

    except Exception as error:
        logger.error(error)
        return geodata

