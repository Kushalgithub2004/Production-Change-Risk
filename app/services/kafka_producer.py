import json
import logging
from aiokafka import AIOKafkaProducer
import os

logger = logging.getLogger(__name__)
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")

class KafkaService:
    producer = None

    @classmethod
    async def get_producer(cls):
        if cls.producer is None:
            cls.producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BROKER_URL,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await cls.producer.start()
        return cls.producer

    @classmethod
    async def stop(cls):
        if cls.producer:
            await cls.producer.stop()
            
async def publish_event(topic: str, message: dict):
    try:
        producer = await KafkaService.get_producer()
        await producer.send_and_wait(topic, message)
        logger.info(f"Published event to {topic}")
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
