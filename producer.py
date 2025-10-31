import json

from pika import ConnectionParameters, BlockingConnection

connection_params = ConnectionParameters(
    host = "localhost",
    port = 5672,
)


def send_to_queue(data: dict):
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="messages")
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            ch.basic_publish(
                exchange="",
                routing_key="messages",
                body=body
            )
            print("OK")

if __name__ == "__main__":
    pass

