import json
from pathlib import Path

from tqdm import tqdm 
from loguru import logger

from src.setup.custom_types import FeedData 
from src.setup.paths import GEOGRAPHICAL_DATA, make_data_directories


class Extractor:
    def __init__(self, feed_name: str, extraction_target: str, feed_data: FeedData | None = None) -> None:
        self.feed_name: str = feed_name.lower()
        self.feed_data: FeedData | None = feed_data 
        self.extraction_target: str = extraction_target

        self.path: Path = self.get_path_to_data()

    def extract_data(self):
        """
        Extract the geographical data associated with each station in the fetched data.

        Args:
            feed_data: data that has been fetched from the ("station_information") feed.
        """
        assert self.feed_data is not None

        if self.extraction_target == "geodata":
            geodata = self.get_saved_data()

            if self.feed_name == "station_information":
                all_station_data = self.feed_data["data"]["stations"]
                
                for station in tqdm(iterable=all_station_data, desc="Collecting station geodata"):
                    station_name = str(station["name"])
                    latitude, longitude = float(station["lat"]), float(station["lon"])
                    geodata[station_name] = [latitude, longitude] 
            
            elif self.feed_name == "free_bike_status":
                all_free_bikes = self.feed_data["data"]["bikes"]

                from src.feature_pipeline.geocoding import reverse_geocode
                for bike in tqdm(iterable=all_free_bikes, desc="Collecting information on free bikes"):
                    latitude, longitude = float(bike["lat"]), float(bike["lon"])
                    
                    if "station_name" not in bike.keys():
                        reverse_geocode(feed_name=self.feed_name, latitude=latitude, longitude=longitude)
                         
            self.save_data(data=geodata)

    def get_path_to_data(self):
        
        paths = {
            "geodata": GEOGRAPHICAL_DATA / f"{self.feed_name}_geodata.json"
        }

        return paths[self.extraction_target]

    def save_data(self, data: dict[str, list[float]]) -> None:
        """
        Save the station geodata that has been created or updated as a json file.

        Args:
            geodata: the data to be saved
            file_path: intended path of the file to be created. 
        """
        logger.info(f"Saving {self.extraction_target} on {self.feed_name.replace("_", " ")} to disk")
        with open(self.path, mode="w") as file:
            json.dump(data, file)

    def get_saved_data(self) -> dict[str, list[float]]:
        """
        Retrieve saved geodata as a dictionary 

        Args:
            file_path: path where this data is to be found.

        Returns:
            dict[str, list[float]]: the geodata that has been loaded. It may also be empty if there is no saved data.
        """
        make_data_directories()

        if Path(self.path).exists():
            logger.info(f"Loading saved {self.extraction_target} related to {self.feed_name}")
            with open(self.path, mode="rb") as file:
                return json.load(file)
        else:
            logger.info(f"There is no saved {self.extraction_target}")
            return {}

