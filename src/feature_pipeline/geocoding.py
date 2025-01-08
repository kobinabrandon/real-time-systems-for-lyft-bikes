import json

from loguru import logger
from geopy import Nominatim, Photon
from geopy.exc import GeocoderUnavailable

from src.setup.config import general_config 
from src.feature_pipeline.extraction import Extractor


def reverse_geocode(feed_name: str, latitude: float, longitude: float)  -> None:
    """
    Take a latitude and longitude, and request its address from Nominatim. If that fails,
    a request will be made to Photon.

    Args:
        latitude: the latitude of the coordinate in question. 
        longitude: the longitude of the coordinate in question. 
        feed_name: name of the feed whose geodata we will be looking for.  
    """
    coordinate = [latitude, longitude]
    extractor = Extractor(feed_name=feed_name, feed_data=None, extraction_target="geodata") 
    geodata = extractor.get_saved_data()

    if coordinate not in geodata.values():
        logger.warning(f"The address of {coordinate} is unknown. Attempting to finding it...")
        try:
            nominatim = Nominatim(user_agent=general_config.email)
            first_try = str(nominatim.reverse(query=coordinate))

            if first_try != "None":
                geodata[first_try] = coordinate

            else:
                logger.warning(f"Nominatim was unable to process {coordinate}. Trying to use Photon")
                photon = Photon(user_agent=general_config.email)
                second_try = str(photon.reverse(query=coordinate))
                
                if second_try != "None":
                    geodata[second_try] = coordinate
                else:
                    logger.error(f"Photon was unable to process {coordinate}.")

            with open(extractor.get_path_to_data(), mode="w") as file:
                json.dump(geodata, file)

        except GeocoderUnavailable as error:
            logger.error(error)
    else:
        logger.warning(f"We already have the address for {coordinate}.")

