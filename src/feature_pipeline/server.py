import json
import asyncio
import requests
import websockets

from loguru import logger
from argparse import ArgumentParser, Namespace
from collections.abc import AsyncGenerator
from websockets.legacy.server import WebSocketServerProtocol 

from src.setup.types import Feed, FeedData
from src.feature_pipeline.feeds import poll, choose_feed


async def poll_for_free_bikes(city_name: str, polling_interval: int) -> FeedData:
    
    while True:
        feeds = await asyncio.to_thread(poll, city_name=city_name, for_feeds = True)
        chosen_feed: Feed = choose_feed(feeds=feeds) 
        feed_url = chosen_feed["url"]  
        
        try:
            response = requests.get(url=feed_url)
            feed_data: FeedData = response.json()   
            print(feed_data)
            return feed_data

        except Exception as error:
            logger.warning(f"Failure to fetch the data on {chosen_feed}. Error: {error}")

        await asyncio.sleep(polling_interval)


async def data_stream(city_name: str, polling_interval: int = 1) -> AsyncGenerator[FeedData]:
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

    async with websockets.serve(handler=handle_client, host="localhost", port=8529):
        logger.info(f"Server started at ws://localhost:8529")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())


