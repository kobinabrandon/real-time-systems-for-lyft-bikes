from loguru import logger
from requests import Response, get

from src.setup.config import use_proper_city_name 
from src.setup.types import FeedCollection, CompleteData 


def get_url(city_name: str) -> str:

    cities_and_feeds = {
        "chicago": "https://gbfs.divvybikes.com/gbfs/2.3/gbfs.json",
        "columbus": "https://gbfs.lyft.com/gbfs/2.3/cmh/gbfs.json",
        "new_york": "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json",
        "washington_dc": "https://gbfs.capitalbikeshare.com/gbfs/2.3/gbfs.json",
        "portland": "https://gbfs.biketownpdx.com/gbfs/2.3/gbfs.json"
    }

    return cities_and_feeds[city_name]

def poll(city_name: str, url: str) -> FeedCollection | None:
    response: Response = get(url)

    if response.status_code == 200:
        data: CompleteData = response.json()
        return data["data"]["en"]
    else:
        proper_city_name = use_proper_city_name(city_name=city_name)
        logger.error(f"No data available for {proper_city_name} at the moment")
        return None


def listen(city_name: str, url: str, polling_interval: int):
    fetched_data : list[FeedCollection] = []

    while True:
        data = poll(city_name, url=url) 
        if data is None:
            logger.warning("No data has been received yet")
            time.sleep(polling_interval)
        else:
            fetched_data.append(data)
            return fetched_data


