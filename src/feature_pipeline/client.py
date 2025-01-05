import asyncio
import websockets 
from loguru import logger

from src.setup.config import websocket_config 


async def client():
    while True:
        async with websockets.connect(f"ws://{websocket_config.host}:{websocket_config.port}") as websocket:
            _ = await websocket.recv()
            logger.success("Received message")


if __name__ == "__main__":
    asyncio.run(client())

