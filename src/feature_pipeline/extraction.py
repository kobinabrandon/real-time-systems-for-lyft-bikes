import json
from tqdm import tqdm
from pathlib import Path
from loguru import logger 

from src.setup.custom_types import FeedData 
from src.setup.paths import GEOGRAPHICAL_DATA, make_data_directories
from src.feature_pipeline.geocoding import reverse_geocode


class GeodataExtractor:
    def __init__(self, city_name: str, feed_name: str, feed_data: FeedData | None = None) -> None:
        self.city_name: str = city_name.lower()
        self.feed_name: str = feed_name.lower()
        self.feed_data: FeedData | None = feed_data 
        self.path_to_station_geodata: Path = GEOGRAPHICAL_DATA / self.city_name / "station_geodata.json" 

        make_data_directories()

    def extract(self):
        """
        Extract the geographical data associated with each station in the fetched data.

        Args:
            feed_data: data that has been fetched from the ("station_information") feed.
        """
        assert self.feed_data is not None

        if self.feed_name == "station_information":
            all_station_data = self.feed_data["data"]["stations"]
            fetched_station_geodata = self.extract_offical_station_geodata(items=all_station_data)  
            saved_station_geodata = self.get_saved_data()
            saved_station_geodata.update(fetched_station_geodata)            
            self.save_data(data=saved_station_geodata)
        
        elif self.feed_name == "free_bike_status":
            all_free_bikes = self.feed_data["data"]["bikes"]
            coordinates = self.extract_coordinates(items=all_free_bikes)
            station_geodata = self.get_saved_data()

            updated_station_geodata = self.get_unknown_addresses(
                coordinates=coordinates, 
                station_geodata=station_geodata
            )

            self.save_data(data=updated_station_geodata)                   

    def get_unknown_addresses(self, coordinates: list[list[float]], station_geodata: dict[str, list[float]]):
        
        for coordinate in tqdm(
            iterable=coordinates,
            desc="Checking for and identifying unknown locations"
        ):
            if coordinate not in station_geodata.values():
                logger.warning(f"{coordinate} is not currently logged")
                breakpoint()
                found_geodata: dict[str, list[float]] = reverse_geocode(latitude=coordinate[0], longitude=coordinate[1])
                station_geodata.update(found_geodata)

        return station_geodata

    def extract_offical_station_geodata(self, items: list[dict[str, int | str]]):
        assert self.feed_name == "station_information"
        return {
                str(item["name"]): [float(item["lat"]), float(item["lon"])] for item in items
        }

    def extract_coordinates(self, items: list[dict[str, int | str]]):
        return [
            [float(item["lat"]), float(item["lon"])] for item in items 
        ] 

    def check_whether_coordinate_is_known(self, coordinate: list[float]):

        if Path(self.path_to_station_geodata).exists():
            with open(self.path_to_station_geodata, mode="r") as file:  
                station_info: dict[str, list[float]] = json.load(file)

            return False if coordinate not in station_info.values() else True

    def save_data(self, data: dict[str, list[float]]) -> None:
        """
        Save the station geodata that has been created or updated as a json file.

        Args:
            geodata: the data to be saved
            file_path: intended path of the file to be created. 
        """
        with open(self.path_to_station_geodata, mode="w") as file:
            json.dump(data, file)

    def get_saved_data(self) -> dict[str, list[float]]:
        """
        Retrieve saved geodata as a dictionary 

        Args:
            file_path: path where this data is to be found.

        Returns:
            dict[str, list[float]]: the geodata that has been loaded. It may also be empty if there is no saved data.
        """
        if Path(self.path_to_station_geodata).exists():
            with open(self.path_to_station_geodata, mode="rb") as file:
                return json.load(file)
        else:
            return {}

