import json
import httpx
from pika import BlockingConnection, ConnectionParameters

connection = BlockingConnection(ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue="weather_request")
channel.queue_declare(queue="weather_response")

print("///")

def get_weather(city: str):
    try:
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10.0,
        ).json()
        if not geo.get("results"):
            return {"error": "City not found"}

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        name = geo["results"][0]["name"]
        country = geo["results"][0]["country"]

        weather = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10.0,
        ).json()

        return {
            "city": name,
            "country": country,
            "temperature": weather["current"]["temperature_2m"],
            "humidity": weather["current"]["relative_humidity_2m"],
            "wind_speed": weather["current"]["wind_speed_10m"],
        }
    except Exception as e:
        return {"error": str(e)}

def on_request(ch, method, props, body):
    city = body.decode("utf-8")
    print(f"[x] Received request for city: {city}")

    result = get_weather(city)
    response_body = json.dumps(result).encode("utf-8")

    ch.basic_publish(
        exchange="",
        routing_key="weather_response",
        body=response_body,
        properties=None,
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"[x] Sent response for city: {city}")

channel.basic_consume(queue="weather_request", on_message_callback=on_request)
channel.start_consuming()
