import asyncio
import websockets 
from loguru import logger


async def client():
    async with websockets.connect("ws://localhost:8525") as websocket:
        message = await websocket.recv()
        logger.success(f"Received: {message}")


if __name__ == "__main__":
    asyncio.run(client())

