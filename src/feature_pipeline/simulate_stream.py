import json
import asyncio
import requests

from collections.abc import AsyncGenerator

from loguru import logger
from websockets.asyncio.server import serve
from websockets.client import ClientProtocol 
from websockets.legacy.server import WebSocketServerProtocol

from src.setup.types import Feed, FeedData
from src.feature_pipeline.feeds import poll, choose_feed


clients: set[ClientProtocol] = set()

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
            logger.error(f"Failure to fetch the data on the '{chosen_feed}' feed. Error: {error}")

        await asyncio.sleep(polling_interval)


async def data_stream(city_name: str, polling_interval: int = 5) -> AsyncGenerator[FeedData]:

    while True:
        yield await poll_for_free_bikes(city_name=city_name, polling_interval=polling_interval)


async def handle_client(city_name: str, websocket: WebSocketServerProtocol):
   
    try:
        async for data in data_stream(city_name=city_name):
            logger.success(f"Received: {data}")
            await websocket.send(json.dumps(data))

    except asyncio.CancelledError as error:
        logger.warning(f"Cancelled : {error}")

    finally:
        await websocket.close()
        logger.warning("Disconnected")


async def main():
    async with serve(handler=handle_client, host="localhost", port=8504):
        logger.info("Server started at ws://localhost:8504")
        await asyncio.Future() 


if __name__ == "__main__":
    asyncio.run(main())
