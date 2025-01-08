import json
from pathlib import Path

from tqdm import tqdm 
from loguru import logger

from src.setup.custom_types import FeedData 
from src.setup.paths import GEOGRAPHICAL_DATA, make_data_directories
from src.feature_pipeline.geocoding import reverse_geocode


class Extractor:
    def __init__(self, city_name: str, feed_name: str, extraction_target: str, feed_data: FeedData | None = None) -> None:
        self.city_name: str = city_name.lower()
        self.feed_name: str = feed_name.lower()
        self.feed_data: FeedData | None = feed_data 
        self.extraction_target: str = extraction_target
        self.path: Path = self.get_path_to_data()

        make_data_directories()

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
                
                for station in tqdm(iterable=all_station_data, desc=f"Collecting station {self.extraction_target}"):
                    station_name = str(station["name"])
                    latitude, longitude = float(station["lat"]), float(station["lon"])
                    geodata[station_name] = [latitude, longitude] 
            
            elif self.feed_name == "free_bike_status":
                all_free_bikes = self.feed_data["data"]["bikes"]
                station_information_path = GEOGRAPHICAL_DATA / self.city_name / "station_information.json"

                for bike in tqdm(iterable=all_free_bikes, desc=f"Collecting {self.extraction_target} on free bikes"):
                    latitude, longitude = float(bike["lat"]), float(bike["lon"])

                    if Path(station_information_path).exists():
                        with open(station_information_path, mode="r") as file:  # Get the station information that is already saved
                            station_info: dict[str, list[float]] = json.load(file)

                        if [latitude, longitude] not in station_info.values():

                            geodata: dict[str, list[float]] = reverse_geocode(
                                city_name=self.city_name, 
                                feed_name=self.feed_name, 
                                latitude=latitude, 
                                longitude=longitude
                            )
                            
                            station_info.update(geodata)
                            with open(station_information_path, mode="r") as file:  
                                station_info: dict[str, list[float]] = json.load(file)
                           
            self.save_data(data=geodata)

    def get_path_to_data(self):
        
       # paths = {
            "geodata": GEOGRAPHICAL_DATA / self.city_name / f"{self.feed_name}_geodata.json"
        }

        return paths[self.extraction_target]

    def save_data(self, data: dict[str, list[float]]) -> None:
        """
        Save the station geodata that has been created or updated as a json file.

        Args:
            geodata: the data to be saved
            file_path: intended path of the file to be created. 
        """
        logger.info(f"Saving {self.extraction_target} from the feed containing {self.feed_name} to disk")
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
        if Path(self.path).exists():
            # logger.info(f"Loading saved {self.extraction_target} related to {self.feed_name}")
            with open(self.path, mode="rb") as file:
                return json.load(file)
        else:
            logger.info(f"There is no saved {self.extraction_target}")
            return {}

