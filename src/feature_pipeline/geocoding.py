import json
from pathlib import Path

from tqdm import tqdm 
from loguru import logger
from geopy import Nominatim, Photon
from geopy.exc import GeocoderUnavailable

from src.setup.config import general_config 
from src.setup.custom_types import FeedData 
from src.setup.paths import GEOGRAPHICAL_DATA, make_data_directories
 

def extract_geodata_from_feed(feed_data: FeedData):

    geodata = get_saved_geodata()    
    all_station_data = feed_data["data"]["stations"]
    
    for station in tqdm(iterable=all_station_data, desc="Collecting station geodata"):
        station_name = str(station["name"])
        coordinate = [float(station["lat"]), float(station["lon"])]
        geodata[station_name] = coordinate

    save_geodata(geodata=geodata)


def reverse_geocode(latitude: float, longitude: float):
     
    coordinate = (latitude, longitude)
    geodata = get_saved_geodata()     
   
    if coordinate not in geodata.values():
        logger.warning(f"The address of {coordinate} is unknown. Attempting to finding it...")
        try:
            nominatim = Nominatim(user_agent=general_config.email)
            first_try = str(nominatim.reverse(query=coordinate))

            if first_try == "None":
                logger.warning(f"Nominatim was unable to process {coordinate}. Trying to use Photon")
                photon = Photon(user_agent=general_config.email)
                second_try = str(photon.reverse(query=coordinate))
                
                geodata[second_try] = coordinate
                
            else:
                geodata[first_try] = coordinate

        except GeocoderUnavailable as error:
            logger.error(error)
    else:
        logger.error(f"We already have the address for {coordinate}.")

    with open(file_path, mode="w") as file:
        json.dump(geodata, file)


def save_geodata(geodata: dict[str, list[float]], file_path: Path = GEOGRAPHICAL_DATA / "station_geodata.json") -> None:
    
    logger.info("Saving station geodata to disk")
    with open(file_path, mode="w") as file:
        json.dump(geodata, file)


def get_saved_geodata(file_path: Path = GEOGRAPHICAL_DATA / "station_geodata.json") -> dict[str, list[float]]:

    make_data_directories()

    if Path(file_path).exists():

        logger.info("Loading saved station geodata")
        with open(file_path, mode="rb") as file:
            return json.load(file)
    else:
        return {}

