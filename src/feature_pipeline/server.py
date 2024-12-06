import json
import asyncio
import requests
import websockets

from loguru import logger
from argparse import ArgumentParser, Namespace
from collections.abc import AsyncGenerator
from websockets.legacy.server import WebSocketServerProtocol 

from src.setup.config import config
from src.setup.types import Feed, FeedData
from src.feature_pipeline.feeds import poll, choose_feed


def is_new_data(fetched_data: list[FeedData]) -> bool:
    data_just_fetched: FeedData = fetched_data[-1]
    penultimate_data: FeedData = fetched_data[-2]
    return False if penultimate_data["last_updated"] == data_just_fetched["last_updated"] else True 


fetched_data: list[FeedData] = []
async def poll_for_free_bikes(city_name: str, polling_interval: int = 5) -> FeedData:

    while True:
        feeds = await asyncio.to_thread(poll, city_name=city_name, for_feeds = True)
        chosen_feed: Feed = choose_feed(feeds=feeds) 
        feed_url = chosen_feed["url"]  
        
        try:
            response = requests.get(url=feed_url)
            feed_data: FeedData = response.json()   
            fetched_data.append(feed_data)
            
            if len(fetched_data) > 1 and not is_new_data(fetched_data=fetched_data): 
                logger.warning("No new data received")
                fetched_data.remove(feed_data)

            else: 
                logger.success("Got new data!")
                return feed_data

        except Exception as error:
            feed_name = chosen_feed["name"]
            logger.warning(f"Failure to fetch the data on '{feed_name}'. Error: {error}")

        await asyncio.sleep(polling_interval)


async def data_stream(city_name: str, polling_interval: int = 5) -> AsyncGenerator[FeedData]:
    yield await poll_for_free_bikes(city_name=city_name, polling_interval = polling_interval)


async def handle_client(websocket: WebSocketServerProtocol):
    
    parser = ArgumentParser()
    _ = parser.add_argument("--city", type=str)
    args: Namespace = parser.parse_args()

    try:
        async for data in data_stream(city_name=args.city):
            await websocket.send(json.dumps(data))

    except asyncio.CancelledError as error:
        logger.error(f"Cancelled: {error}")
    

async def main():

    async with websockets.serve(handler=handle_client, host=config.host, port=config.port):
        logger.info(f"Server started at ws://{config.host}:{config.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

