import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
TOPIC = "pr_events"

async def consume():
    # Retry connecting to Kafka to allow time for the broker to start in Docker
    while True:
        try:
            consumer = AIOKafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BROKER_URL,
                group_id="risk_analysis_group",
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            await consumer.start()
            break
        except Exception as e:
            logger.warning(f"Waiting for Kafka broker... {e}")
            await asyncio.sleep(5)
            
    logger.info("Kafka Worker started. Listening for PR events...")
    
    try:
        async for msg in consumer:
            payload = msg.value
            pr_number = payload.get("pull_request", {}).get("number", "Unknown")
            logger.info(f"Worker received PR {pr_number} event. Processing asynchronously...")
            
            # Here we would do the actual diff extraction and ML inference
            # simulating a long running heavy ML task
            await asyncio.sleep(2)
            
            logger.info(f"Worker successfully processed PR {pr_number}")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())
