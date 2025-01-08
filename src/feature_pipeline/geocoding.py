import json

from loguru import logger
from geopy import Nominatim, Photon
from geopy.exc import GeocoderUnavailable
from collections.abc import AsyncGenerator

from src.setup.config import general_config 
from src.setup.custom_types import FeedData
from src.feature_pipeline.server import poll_feed
from src.feature_pipeline.extraction import Extractor


async def get_station_geodata(city_name: str, feed_name: str = "station_information") -> AsyncGenerator[FeedData]:
    yield await poll_feed(feed_name=feed_name, city_name=city_name)


def reverse_geocode(city_name: str, feed_name: str, latitude: float, longitude: float) -> dict[str, list[float]]: 
    """
    Take a latitude and longitude, and request its address from Nominatim. If that fails,
    a request will be made to Photon.

    Args:
        latitude: the latitude of the coordinate in question. 
        longitude: the longitude of the coordinate in question. 
        feed_name: name of the feed whose geodata we will be looking for.  
    """
    extractor = Extractor(city_name=city_name, feed_name=feed_name, feed_data=None, extraction_target="geodata") 
    geodata = extractor.get_saved_data()
    
    coordinate = [latitude, longitude]
    logger.warning(f"The address of {coordinate} is unknown. Attempting to find it...")
    if coordinate not in geodata.values():
        try:
            nominatim = Nominatim(user_agent=general_config.email)
            first_try = str(nominatim.reverse(query=coordinate))

            if first_try != "None":
                geodata[first_try] = coordinate
            else:
                photon = Photon(user_agent=general_config.email)
                second_try = str(photon.reverse(query=coordinate))  # If this returns "None", we will look for it later.
                geodata[second_try] = coordinate  
                
            with open(extractor.get_path_to_data(), mode="w") as file:
                json.dump(geodata, file)

            return geodata

        except GeocoderUnavailable as error:
            logger.error(error)
            return geodata
    else:
        logger.success(f"We already have the address for {coordinate}.")
        return geodata

