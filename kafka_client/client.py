import asyncio
import logging
from abc import abstractmethod, ABC

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

logger = logging.getLogger(__name__)


class Client(ABC):
    def __init__(self, service_name: str, bootstrap_servers: str, group_id: str, auto_offset_reset: str):
        """Initialize the Kafka client with connection settings.

        Args:
            service_name (str): Name of the app or service this Client is run from (used in logging statements)
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers (e.g., 'localhost:9092').
            group_id (str): Consumer group ID for Kafka consumer.
            auto_offset_reset (str): Offset reset policy ('earliest', 'latest', or 'none').
        """
        self.service_name = service_name
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset

    async def _build_consumer(self, *topics: str):
        """Create a Kafka consumer for the specified topics.

        Args:
            *topics (str): One or more Kafka topic names to subscribe to.

        Returns:
            AIOKafkaConsumer: Configured Kafka consumer instance.
        """
        return AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset
        )

    async def _build_producer(self):
        """Create a Kafka producer for sending messages.

        Returns:
            AIOKafkaProducer: Configured Kafka producer instance.
        """
        return AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)

    async def wait_for_start(self, max_retries: int = 15, retry_delay: int = 3):
        """Wait for Kafka to become available and start the client(s).

        Repeatedly attempts to connect to Kafka until successful or max retries are reached.

        Args:
            max_retries (int, optional): Maximum number of connection attempts. Defaults to 15.
            retry_delay (int, optional): Delay (in seconds) between retries. Defaults to 3.

        Raises:
            KafkaConnectionError: If Kafka is not available after max_retries attempts.
        """
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)

        for attempt in range(max_retries):
            try:
                await producer.start()
                await producer.stop()
                logger.info(f"{self.service_name} is ready to accept Kafka connections")

                return await self._start()

            except KafkaConnectionError as e:
                logger.warning(f"Kafka not ready (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt + 1 == max_retries:
                    raise KafkaConnectionError(f"Kafka not available after {max_retries} retries")

                await asyncio.sleep(retry_delay)

    @abstractmethod
    async def _start(self):
        """Initialize and start Kafka consumers and producers.

        Subclasses must implement this method to define specific consumer/producer startup logic.

        Returns:
            None
        """
