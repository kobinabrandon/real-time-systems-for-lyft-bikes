from time import sleep
from loguru import logger
from requests import Response, get
from argparse import ArgumentParser
from requests.exceptions import RequestException

from src.setup.config import use_proper_city_name 
from src.setup.types import Feed, DataFromChosenFeed, LanguageOptions


def get_base_url_for_city(city_name: str) -> str:

    cities_and_feeds = {
        "chicago": "https://gbfs.divvybikes.com/gbfs/2.3/gbfs.json",
        "columbus": "https://gbfs.lyft.com/gbfs/2.3/cmh/gbfs.json",
        "new_york": "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json",
        "washington_dc": "https://gbfs.capitalbikeshare.com/gbfs/2.3/gbfs.json",
        "portland": "https://gbfs.biketownpdx.com/gbfs/2.3/gbfs.json"
    }

    return cities_and_feeds[city_name]


async def poll_for_base_data(city_name: str, url: str) -> list[Feed] | None:

    try:
        response: Response = get(url)
        if response.status_code == 200:
            data: DataFromChosenFeed = response.json()
            list_of_feeds: list[Feed] = data["data"]["en"]["feeds"]

            all_feeds: LanguageOptions = data["data"]

            return list_of_feeds
        else:
            proper_city_name = use_proper_city_name(city_name=city_name)
            logger.error(f"No data available for {proper_city_name}. Status code: {response.status_code}")
            return None

    except RequestException as error:
        logger.error(f"Could not fetch the data for {use_proper_city_name(city_name=city_name)}")
        return None

    
async def poll_for_chosen_feed(city_name: str, url: str) -> list[Feed] | DataFromChosenFeed | None:
    
    try:
        response: Response = get(url)
        if response.status_code == 200:
            data: BaseData = response.json()
            list_of_feeds: list[Feed] = data["data"]["en"]["feeds"]
            return list_of_feeds
        else:
            proper_city_name = use_proper_city_name(city_name=city_name)
            logger.error(f"No data available for {proper_city_name}. Status code: {response.status_code}")
            return None

    except RequestException as error:
        logger.error(f"Could not fetch the data for {use_proper_city_name(city_name=city_name)}")
        return None


async def get_all_feeds(city_name: str, url: str, polling_interval: int)-> list[Feed] | None:

    while True:
        feeds = poll_for_base_data(city_name, url=url) 
        if feeds == None:
            logger.warning("No data has been received yet")
            sleep(polling_interval)
        else:
            return feeds 


def choose_feed(feeds: list[Feed], feed_name: str="free_bike_status") -> Feed | None: 

    for feed in feeds:
        try:
            if feed.name == feed_name: 
               return feed
        except Exception as error:
            logger.error(error)
            return None 


def get_url_for_chosen_feed(feed: Feed) -> str:
    return feed.url


if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--city", type=str)

    args = parser.parse_args()
    url = get_base_url_for_city(city_name=args.city)
    data_on_free_bikes: DataFromChosenFeed = poll_for_free_bikes(city_name=args.city, url=url, polling_interval=5)
    breakpoint()
