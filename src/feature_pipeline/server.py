import json
import asyncio
import requests
import websockets

from loguru import logger
from argparse import ArgumentParser, Namespace
from collections.abc import AsyncGenerator
from websockets.legacy.server import WebSocketServerProtocol

from src.setup.config import websocket_config 
from src.setup.custom_types import FeedData
from src.setup.paths import make_data_directories
from src.feature_pipeline.feeds import choose_feed, poll


collected_data: list[FeedData] = []
async def poll_feed(feed_name: str, city_name: str, polling_interval: int = 5) -> FeedData:

    while True:
        all_feeds = await asyncio.to_thread(poll, city_name=city_name, for_feeds=True)
        chosen_feed: Feed = choose_feed(feed_name=feed_name, feeds=all_feeds) 
        feed_url: str = chosen_feed["url"]  

        response = requests.get(url=feed_url)

        if response.status_code != 200:
            logger.error(f"Failure to fetch the data on '{feed_name}'. Status code: {response.status_code}")
        else:
            feed_data: FeedData = response.json()   
            collected_data.append(feed_data)
            
            if len(collected_data) > 1 and not is_new_data(collected_data=collected_data): 
                logger.warning("No new data received")
                collected_data.remove(feed_data)
            else: 
                from src.feature_pipeline.extraction import Extractor
                logger.success("Got new data!")

                if feed_name in ["station_information", "free_bike_status"]:
                    logger.info("Extracting geodata...")
                    
                    extractor = Extractor(
                        city_name=city_name, 
                        feed_name=feed_name, 
                        feed_data=feed_data, 
                        extraction_target="geodata"
                    )

                    extractor.extract_data()
                    return feed_data

        await asyncio.sleep(polling_interval)


def set_arguments() -> Namespace:
    
    parser = ArgumentParser()
    _ = parser.add_argument("--feed_name", type=str)
    _ = parser.add_argument("--city_name", type=str)
    return parser.parse_args()


def is_new_data(collected_data: list[FeedData]) -> bool:
    """
    Check whether the data that has been fetched contains data that is new when compared to the 
    data that waas last connected. 
    
    Args:
        collected_data: the data that has been collected from the websocket connection. 

    Returns:
        bool: whether the data contains new data or not.
    """
    data_just_fetched: FeedData = collected_data[-1]
    penultimate_data: FeedData = collected_data[-2]
    return False if penultimate_data["last_updated"] == data_just_fetched["last_updated"] else True 


async def data_stream(feed_name: str, city_name: str, polling_interval: int = 5) -> AsyncGenerator[FeedData]:
    yield await poll_feed(feed_name=feed_name, city_name=city_name, polling_interval = polling_interval)


async def handle_client(websocket: WebSocketServerProtocol):
    
    args = set_arguments()

    try:
        async for data in data_stream(feed_name=args.feed_name, city_name=args.city_name):
            await websocket.send(json.dumps(data))

    except asyncio.CancelledError as error:
        logger.error(f"Cancelled: {error}")
    

async def main():

    async with websockets.serve(handler=handle_client, host=websocket_config.host, port=websocket_config.port):
        logger.info(f"Server started at ws://{websocket_config.host}:{websocket_config.port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

