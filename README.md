# kafka-client
[![Python versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-green)](https://www.python.org/downloads/)

A simple and lightweight wrapper around `aiokafka` to streamline Kafka integration in your Python projects, whether big or small.

Just inherit the `Client` class, define your initialization logic, and you're ready to produce and consume Kafka messages with ease!

---

## Features

- **Simple Abstraction**: Extend the `Client` class to quickly set up Kafka producers and consumers.
- **Asyncio-Friendly**: Built for seamless integration with Python's `asyncio` ecosystem.
- **Lightweight**: Minimal dependencies and straightforward API.

---

## Installation

Install the package via pip:

```bash
pip install https://github.com/Karnosio/kafka-client/archive/refs/heads/main.zip
```

---

## Quick Start
Here’s an example of how to use the `kafka-client` library by extending the `Client` class.

```python
import asyncio
from kafka_client import Client
from typing import Optional
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


class KafkaBroker(Client):
    def __init__(self, bootstrap_servers: str, group_id: str, auto_offset_reset: str):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        super().__init__(
            service_name="Broker",
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset
        )

    async def _start(self):
        self.consumer = await self._build_consumer("test.topic")  # pass topics you want to listen to
        await self.consumer.start()

        self.producer = await self._build_producer()
        await self.producer.start()

    async def listen_to_consumer(self):
        async for msg in self.consumer:  # Runs indefinitely
            print(f"Got a new message from Kafka: {msg.key}: {msg.value} | Offset {msg.offset}")

    async def send_data_to_producer(self):
        while True:
            await self.producer.send_and_wait(topic="test.topic2", value=b"test_data")
            await asyncio.sleep(1)
```

### Usage Example

Run your Kafka client using `asyncio`:

```python
import asyncio

async def main():
    broker = KafkaBroker(bootstrap_servers="kafka:9092", group_id="my_group", auto_reset_offset="latest")
    
    # Run this at the start of your program, this will ensure that Kafka is ready to accept connections
    await broker.wait_for_start()
    
    # Then run your consumers and producers
    await asyncio.gather(
        await broker.listen_to_consumer(),
        await broker.send_data_to_producer()
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration
The `Client` class accepts the following parameters:

- `service_name`: A name for your Kafka client instance.
- `bootstrap_servers`: Kafka bootstrap servers (e.g., `localhost:9092`).
- `group_id`: Consumer group ID for Kafka consumers.
- `auto_offset_reset`: Offset reset policy (`earliest`, `latest`, or `none`).

You can pass these settings directly or through any other method that fits your project.

---

## License
This project is licensed under the MIT License.