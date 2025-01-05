import json
import asyncio
import requests
import websockets

from loguru import logger
from argparse import ArgumentParser, Namespace
from collections.abc import AsyncGenerator
from websockets.legacy.server import WebSocketServerProtocol 

from src.setup.config import websocket_config 
from src.setup.paths import RAW_DATA_DIR, make_data_directories
from src.setup.custom_types import Feed, FeedData
from src.feature_pipeline.feeds import poll, choose_feed


collected_data: list[FeedData] = []
async def poll_for_free_bikes(city_name: str, polling_interval: int = 5) -> FeedData:

    while True:
        all_feeds = await asyncio.to_thread(poll, city_name=city_name, for_feeds = True)
        chosen_feed: Feed = choose_feed(feeds=all_feeds) 
        feed_url = chosen_feed["url"]  
        
        try:
            response = requests.get(url=feed_url)
            feed_data: FeedData = response.json()   
            collected_data.append(feed_data)
            
            if len(collected_data) > 1 and not is_new_data(collected_data=collected_data): 
                logger.warning("No new data received")
                collected_data.remove(feed_data)

            else: 
                logger.success("Got new data!")
                return feed_data

        except Exception as error:
            feed_name = chosen_feed["name"]
            logger.warning(f"Failure to fetch the data on '{feed_name}'. Error: {error}")

        await asyncio.sleep(polling_interval)


def is_new_data(collected_data: list[FeedData]) -> bool:
    data_just_fetched: FeedData = collected_data[-1]
    penultimate_data: FeedData = collected_data[-2]
    return False if penultimate_data["last_updated"] == data_just_fetched["last_updated"] else True 


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

    make_data_directories()

    async with websockets.serve(handler=handle_client, host=websocket_config.host, port=websocket_config.port):
        logger.info(f"Server started at ws://{websocket_config.host}:{websocket_config.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

