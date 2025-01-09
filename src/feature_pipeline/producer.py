import asyncio
from loguru import logger
from quixstreams import Application 

from src.setup.config import redpanda_config
from src.feature_pipeline.server import poll_feed 


async def produce_bikes(
    city_name: str,
    feed_name: str = "free_bike_status",
    kafka_broker_address: str = redpanda_config.kafka_broker_address
):
    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=feed_name, value_serializer="json")

    with app.get_producer() as producer:
        while True:
            feed_data = await poll_feed(feed_name=feed_name, city_name=city_name) 
            message = topic.serialize(key=f"{city_name}_{feed_name}", value=feed_data)
            producer.produce(topic=topic.name, value=message.value, key=message.key)

            logger.info(f"Pushed data to Kafka: {feed_data}")

if __name__ == "__main__":
    asyncio.run(
        produce_bikes(city_name="portland")
    )

