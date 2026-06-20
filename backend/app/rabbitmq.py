import json
import logging
import aio_pika
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class RabbitMQSettings(BaseSettings):
    RABBITMQ_URL: str = "amqp://rrtm:rrtm@localhost:5672/"

settings = RabbitMQSettings()

class RabbitMQManager:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            # Declare the queue to ensure it exists
            await self.channel.declare_queue("worker_tasks", durable=True)
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    async def close(self):
        """Close connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")

    async def publish_task(self, issue_id: int):
        """Publish a new task to the queue."""
        if not self.channel:
            await self.connect()

        try:
            message_body = json.dumps({"issue_id": issue_id}).encode()
            message = aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await self.channel.default_exchange.publish(
                message,
                routing_key="worker_tasks"
            )
            logger.info(f"Published task for issue_id={issue_id} to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to publish task: {e}")

rabbitmq_manager = RabbitMQManager()
