import json
from pika import BlockingConnection, ConnectionParameters

connection_params = ConnectionParameters(
    host="localhost",
    port=5672,
)

def process_message(ch, method, properties, body):
    print(f"Received message: {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="messages")
            ch.basic_consume(queue="messages", on_message_callback=process_message)
            ch.start_consuming()

if __name__ == "__main__":
    main()
