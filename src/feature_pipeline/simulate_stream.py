import time 
import json 
import asyncio
import websockets 
from websockets.client import ClientProtocol 

from src.feature_pipeline.feeds import get_all_feeds, poll, choose_feed, get_url_for_chosen_feed
from src.setup.types import DataFromChosenFeed


class StreamSimulator:

    def __init__(self) -> None:
        self.clients = set()

    async def poll_for_free_bikes(self, city_name: str, url: str, polling_interval: int) -> None:
    
        details_of_all_feeds = get_all_feeds(city_name=city_name, url=url, polling_interval=polling_interval)    
        chosen_feed: Feed = choose_feed(feeds=details_of_all_feeds) 
        feed_url = get_url_for_chosen_feed(feed=chosen_feed)

        while True:
            feed_data = await asyncio.to_thread(func=poll, city_name=city_name, is_base_url=False, url=feed_url)
            if feed_data:
                data_on_free_bikes: DataFromChosenFeed = feed_data["data"]["bikes"]
                message = json.dumps(data_on_free_bikes)
                
                _ = await asyncio.gather(
                    *(client.send(message) for client in self.clients)
                )

            else:
                logger.warning(f"Failure to fetch the data on {chosen_feed}")

            await asyncio.sleep(polling_interval)

    async def handle_client()
