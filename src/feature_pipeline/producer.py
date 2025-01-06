from quixstreams import Application 
from src.feature_pipeline.server import poll_chosen_feed
    

def get_station_names()


def produce_trades(
    kafka_broker_address: str,
    kafka_topic: str,
    city_name: str,
    id: str
):
    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=kafka_topic, value_serializer="json")

    with app.get_producer() as producer:
        while True:
            free_bike = poll_for_free_bikes(city_name=city_name) 
            message = topic.serialize(key=id, value=free_bike)

            producer.produce(topic=topic.name, value=message.value, key=message.key)

