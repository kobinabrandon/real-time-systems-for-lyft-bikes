import json
from tqdm import tqdm
from pathlib import Path

from src.setup.custom_types import FeedData 
from src.feature_pipeline.geocoding import reverse_geocode
from src.setup.paths import GEOGRAPHICAL_DATA, make_data_directories

from src.setup.custom_types import (
    FoundGeodata, 
    BikeInformation, 
    ListOfCoordinates, 
    StationInformation, 
    OfficialStationGeodata
)


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
            all_station_data: StationInformation = self.feed_data["data"]["stations"]
            fetched_official_station_geodata: OfficialStationGeodata = self.update_official_station_geodata(items=all_station_data)  
            self.save_data(data=fetched_official_station_geodata, official=True)
                    
        elif self.feed_name == "free_bike_status":
            all_free_bikes: BikeInformation = self.feed_data["data"]["bikes"]
            breakpoint()
            coordinates_of_free_bikes: ListOfCoordinates = self.extract_coordinates(items=all_free_bikes)

            identified_geodata_of_free_bikes: FoundGeodata = self.get_unknown_addresses(coordinates=coordinates_of_free_bikes)

            self.save_data(data=identified_geodata_of_free_bikes, official=False)                   
    
    def get_unknown_addresses(self, coordinates: ListOfCoordinates) -> FoundGeodata: 
        """
        Takes the geodata that from the "station_information" feed and checks whether each of the given 
        coordinate is already in the data from that feed. If it isn't, reverse geocoding will be used to obtain 
        an address for it. These addresses and their coordinates will then be returned.  

        Args:
            coordinates: the coordinates whose addresses we will be attempting to find 
            saved_station_geodata: the geodata obtained from the "station_information" feed 

        Returns:
            FoundGeodata: a dictionary of coordinates and the addessses that were obtained through reverse geocoding
        """
        all_found_geodata: FoundGeodata = {}
        saved_official_station_geodata: OfficialStationGeodata = self.get_saved_data(official=True)

        for coordinate in tqdm( 
            iterable=coordinates,
            desc="Checking for and identifying unknown locations"
        ):
            if coordinate not in saved_official_station_geodata:
                found_geodata: FoundGeodata = reverse_geocode(latitude=coordinate[0], longitude=coordinate[1])
                all_found_geodata.update(found_geodata)

        return all_found_geodata 
        
    def update_official_station_geodata(self, items: StationInformation) -> OfficialStationGeodata: 
        """
        Goes through each element of the geodata from the "station_information" feed, extracts the name, address, and 
        coordinate of each entry. Any saved geodata will then be loaded, so that if each geodata element is not already in 
        the saved geodata, it will be included. After all this, the updated geodata is then saved. 

        Args:
            items: all of the geodata fetched from the feed. 

        Returns:
           OfficialStationGeodata: all of the geodata that was made available by the "station_information" feed. 
        """
        assert self.feed_name == "station_information"
        saved_data: OfficialStationGeodata = self.get_saved_data(official=True)

        for item in items:
            extracted_geodata = {
                "name": item["name"],
                "address": item["address"],
                "coordinate": [item["lat"], item["lon"]] 
            }
            
            # Ignore duplicates
            if extracted_geodata not in saved_data:
                saved_data.append(extracted_geodata)
 
        return saved_data 

    def extract_coordinates(self, items: StationInformation) -> ListOfCoordinates: 
        """
        Extracts the coordinates for each element of the feed and puts them in a list which is returned.

        Args:
            items: an list of dictionaries that contains all of the specific desired information obtained from the feed. 

        Returns:
           ListOfCoordinates: desired list of coordinates 
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
           bool: whether or not the coordinate is contained in the station geodata fetched from the primary source. 
        """
        with open(self.path_to_official_geodata, mode="r") as file:  
            station_info: FoundGeodata = json.load(file)

        return False if coordinate not in station_info.values() else True

    def save_data(self, data: FoundGeodata | OfficialStationGeodata, official: bool) -> None:
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

    def get_saved_data(self, official: bool) -> OfficialStationGeodata: 
        """
        Retrieve saved geodata as a dictionary 

        Args:
            official: whether the data to be saved is from the station_information feed 
                      (which I deem to be the "official" source) or not. 

        Returns:
            OfficialStationGeodata: the geodata that has been loaded. If there is no saved data, an empty list will be returned.
        """
        path = self.path_to_official_geodata if official else self.path_to_other_geodata 
        if Path(path).exists():
            with open(path, mode="rb") as file:
                return json.load(file)
        else:
            return [] 

