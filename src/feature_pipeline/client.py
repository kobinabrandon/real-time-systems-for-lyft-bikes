import asyncio
import websockets 
from loguru import logger


async def client():
    while True:
        async with websockets.connect("ws://localhost:8529") as websocket:
            _ = await websocket.recv()
            logger.success("Received: message")


if __name__ == "__main__":
    asyncio.run(client())

