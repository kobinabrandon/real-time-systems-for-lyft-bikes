from loguru import logger
from requests import Response, get
from requests.exceptions import RequestException

from src.setup.config import use_proper_city_name 
from src.setup.custom_types import Feed, AllData 


def get_base_url_for_city(city_name: str) -> str:

    cities_and_feeds = {
        "chicago": "https://gbfs.divvybikes.com/gbfs/2.3/gbfs.json",
        "columbus": "https://gbfs.lyft.com/gbfs/2.3/cmh/gbfs.json",
        "new_york": "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json",
        "washington_dc": "https://gbfs.capitalbikeshare.com/gbfs/2.3/gbfs.json",
        "portland": "https://gbfs.biketownpdx.com/gbfs/2.3/gbfs.json"
    }

    return cities_and_feeds[city_name]


def poll(city_name: str, for_feeds: bool) -> AllData | list[Feed] | None:
    
    try:
        base_url = get_base_url_for_city(city_name=city_name)
        response: Response = get(base_url)

        if response.status_code == 200:
            data: AllData = response.json()
            
            if for_feeds:
                list_of_feeds: list[Feed] = data["data"]["en"]["feeds"]
                return list_of_feeds
            else:
               return data 
        else:
            proper_city_name = use_proper_city_name(city_name=city_name)
            logger.error(f"No data available for {proper_city_name}. Status code: {response.status_code}")
            return None

    except RequestException as error:
        logger.warning(f"Could not fetch the data for {use_proper_city_name(city_name=city_name)}")
        logger.error(error)
        return None


def choose_feed(feeds: list[Feed], feed_name: str) -> Feed | None: 
    
    for feed in feeds:
        try:
            if feed["name"] == feed_name: 
               return feed
        except Exception as error:
            logger.error(error)
            return None 

