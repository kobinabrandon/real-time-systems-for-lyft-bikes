import json 
import asyncio
import requests
from socket import create_connection

from websockets.asyncio.server import serve
from websockets.asyncio.client import connect
from websockets.client import ClientConnection, ClientProtocol

from src.setup.types import Feed
from src.feature_pipeline.feeds import poll, choose_feed, get_base_url_for_city


clients = set()
async def poll_for_free_bikes(city_name: str, polling_interval: int = 5) -> None:
    
    while True:
        feeds = await asyncio.to_thread(poll, city_name=city_name, for_feeds = True)
        chosen_feed: Feed = choose_feed(feeds=feeds) 
        feed_url = chosen_feed["url"]  
        response = requests.get(url=feed_url)
        feed_data: dict[str, dict[str, list[dict[str, int|str]]]] = response.json()

        if feed_data:
            message = json.dumps(feed_data)
            await asyncio.gather(*(client.send(message) for client in clients))
        else:
            logger.warning(f"Failure to fetch the data on {chosen_feed}")

        await asyncio.sleep(polling_interval)


# async def handle_client():


poll_for_free_bikes(city_name="chicago", url=get_base_url_for_city(city_name="chicago"), polling_interval=5)



