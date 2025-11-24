from contextlib import contextmanager
from typing import Generator, Optional

import pika

from config import get_rabbitmq_url


class RabbitMQClient:
    def __init__(self, url: Optional[str] = None) -> None:
        self.url = url or get_rabbitmq_url()
        if not self.url:
            raise ValueError("RabbitMQ URL missing; set RABBITMQ_URL environment variable.")

        self.parameters = pika.URLParameters(self.url)

    @contextmanager
    def connection(self) -> Generator[pika.BlockingConnection, None, None]:
        """Context manager that yields a blocking connection."""
        connection = pika.BlockingConnection(self.parameters)
        try:
            yield connection
        finally:
            if connection.is_open:
                connection.close()

    @contextmanager
    def channel(self) -> Generator[pika.channel.Channel, None, None]:
        """Context manager that yields a channel, closing it afterwards."""
        with self.connection() as connection:
            channel = connection.channel()
            try:
                yield channel
            finally:
                if channel.is_open:
                    channel.close()

    def publish(
        self,
        queue_name: str,
        body: bytes,
        durable: bool = True,
    ) -> None:
        """Minimal publisher that declares a queue and sends a message."""
        with self.channel() as channel:
            channel.queue_declare(queue=queue_name, durable=durable)
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2 if durable else 1),
            )

