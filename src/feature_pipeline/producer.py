import asyncio
from quixstreams import Application 

from src.setup.config import redpanda_config
from src.feature_pipeline.server import poll_feed 
from src.feature_pipeline.geocoding import Extractor 


async def produce_bikes(
    id: str,
    city_name: str,
    feed_name: str = "free_bike_status",
    kafka_broker_address: str = redpanda_config.kafka_broker_address
):
    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=feed_name, value_serializer="json")

    with app.get_producer() as producer:
        while True:
            free_bike_data = await poll_feed(feed_name=feed_name, city_name=city_name) 

            breakpoint()
            message = topic.serialize(key=id, value=free_bike_data)

            breakpoint()

            producer.produce(topic=topic.name, value=message.value, key=message.key)


if __name__ == "__main__":
    asyncio.run(
        produce_bikes(city_name="portland", id="sdfs")
    )
