import json
from pika import BlockingConnection, ConnectionParameters

connection_params = ConnectionParameters(
    host="localhost",
    port=5672,
)

def process_message(ch, method, properties, body):
    print(f"Received message: {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

#def process_message(ch, method, properties, body):
#   data = json.loads(body.decode("utf-8"))
#    print(f"New data:")
 #   print(f"City: {data['city']}")
  #  print(f"Country: {data['country']}")
   # print(f"Temperature: {data['current']['temperature_2m']}°C")
    #print(f"Humidity: {data['current']['relative_humidity_2m']}%")

    #ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="hello")
            ch.basic_consume(queue="hello", on_message_callback=process_message)
            ch.start_consuming()

if __name__ == "__main__":
    main()
