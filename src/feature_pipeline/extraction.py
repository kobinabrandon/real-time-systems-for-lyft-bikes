import json
from tqdm import tqdm
from pathlib import Path

from src.setup.custom_types import FeedData 
from src.feature_pipeline.geocoding import reverse_geocode
from src.setup.paths import GEOGRAPHICAL_DATA, make_data_directories


class GeodataExtractor:
    def __init__(self, city_name: str, feed_name: str, feed_data: FeedData | None = None) -> None:
        """
        Extracts geodata from a specific feed from a particular city.  

        Args:
            city_name: the name of the city whose data we are sourcing 
            feed_name: the name of the feed which we will be producing data 
            feed_data: data that has been fetched from the ("station_information") feed. 
        """
        self.city_name: str = city_name.lower()
        self.feed_name: str = feed_name.lower()
        self.feed_data: FeedData | None = feed_data 
        self.path_to_other_geodata: Path = GEOGRAPHICAL_DATA / self.city_name / f"{feed_name}_geodata.json" 
        self.path_to_official_geodata: Path = GEOGRAPHICAL_DATA / self.city_name / "official_station_geodata.json" 

        make_data_directories()

    def extract(self):
        """
        Extract the geographical data associated with each station in the fetched data.
        """
        assert self.feed_data is not None

        if self.feed_name == "station_information":
            all_station_data = self.feed_data["data"]["stations"]
            fetched_official_station_geodata = self.extract_official_station_geodata(items=all_station_data)  
            saved_official_station_geodata = self.get_saved_data(official=True)
            
            if len(saved_official_station_geodata) > 0:
                saved_official_station_geodata.append(fetched_official_station_geodata)
            else:
                saved_official_station_geodata.extend(fetched_official_station_geodata)

            self.save_data(data=saved_official_station_geodata, official=True)
        
        elif self.feed_name == "free_bike_status":
            all_free_bikes = self.feed_data["data"]["bikes"]
            coordinates_of_free_bikes = self.extract_coordinates(items=all_free_bikes)
            saved_official_station_geodata = self.get_saved_data(official=True)

            identified_geodata_of_free_bikes = self.get_unknown_addresses(
                coordinates=coordinates_of_free_bikes, 
                saved_station_geodata=saved_official_station_geodata
            )

            self.save_data(data=identified_geodata_of_free_bikes, official=False)                   
    
    @staticmethod
    def get_unknown_addresses(
        coordinates: list[list[float]], 
        saved_station_geodata: dict[str, list[float]]
    ) -> dict[str, list[float]]:
        """
        Takes the geodata that from the "station_information" feed and checks whether each of the given 
        coordinate is already in the data from that feed. If it isn't, reverse geocoding will be used to obtain 
        an address for it. These addresses and their coordinates will then be returned.  

        Args:
            coordinates: the coordinates that we will be attempting to find the addessses for
            saved_station_geodata: the geodata obtained from the "station_information" feed 

        Returns:
           dict[str, list[float]]: a dictionary of coordinates and the addessses that were obtained from through
                                   reverse geocoding
        """
        all_found_geodata: dict[str, list[float]] = {}

        for coordinate in tqdm(
            iterable=coordinates,
            desc="Checking for and identifying unknown locations"
        ):
            if coordinate not in saved_station_geodata.values():
                found_geodata: dict[str, list[float]] = reverse_geocode(latitude=coordinate[0], longitude=coordinate[1])
                all_found_geodata.update(found_geodata)

        return all_found_geodata 

    def extract_official_station_geodata(self, items: list[dict[str, int | str]]) -> list[dict[str, str | list[float]]]:
        """
        Goes through each element of the geodata from the "station_information" feed, and extracts the name, address, and 
        coordinate of each entry.

        Args:
            items: all of the geodata fetched from the feed. 

        Returns:
           dict[str, str | list[float]]: all of the geodata that was made available by the "station_information" feed. 
        """
        assert self.feed_name == "station_information"
        all_official_station_geodata: list[dict[str, str | list[float]]] = []

        for item in items:
            extracted_geodata = {
                "name": str(item["name"]),
                "address": str(item["address"]),
                "coordinate": [float(item["lat"]), float(item["lon"])] 
            }

            all_official_station_geodata.append(extracted_geodata) 

        return all_official_station_geodata

    def extract_coordinates(self, items: list[dict[str, int | str]]) -> list[list[float]]:
        """
        Extracts the coordinates for each element of the feed and puts them in a list which is returned.

        Args:
            items: an list of dictionaries that contains all of the specific desired information obtained from the feed. 

        Returns:
           list[list[float]]: desired list of coordinates 
        """
        return [
            [float(item["lat"]), float(item["lon"])] for item in items 
        ] 

    def check_whether_coordinate_is_known(self, coordinate: list[float]) -> bool:
        """
        Returns "True" if the given coordinate is already contained in the station geodata from the "station_information" feed, 
        and "False" if it isn't.

        Args:
            coordinate: the coordinate to be sought after. 

        Returns:
            
        """
        with open(self.path_to_official_geodata, mode="r") as file:  
            station_info: dict[str, list[float]] = json.load(file)

        return False if coordinate not in station_info.values() else True

    def save_data(self, data: list[dict[str, list[float]]] | list[dict[str, str | list[float]]], official: bool) -> None:
        """
        Save the station geodata that has been created or updated as a json file.

        Args:
            data: the data to be saved
            official: whether the data to be saved is from the station_information feed 
                      (which I deem to be the "official" source) or not. 
        """
        path = self.path_to_official_geodata if official else self.path_to_other_geodata 
        with open(path, mode="w") as file:
            json.dump(data, file)

    def get_saved_data(self, official: bool) -> list[dict[str, list[float]]] | list[dict[str, str | list[float]]]:
        """
        Retrieve saved geodata as a dictionary 

        Args:
            official: whether the data to be saved is from the station_information feed 
                      (which I deem to be the "official" source) or not. 

        Returns:
            list[dict[str, str | list[float]]]: the geodata that has been loaded. It may also be empty if 
                                                there is no saved data.
        """
        path = self.path_to_official_geodata if official else self.path_to_other_geodata 
        if Path(path).exists():
            with open(path, mode="rb") as file:
                return json.load(file)
        else:
            return [] 

