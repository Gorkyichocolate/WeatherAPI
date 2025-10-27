import json
import os
from fastapi import FastAPI, HTTPException, Query
import httpx

app = FastAPI()

def weather_json(data):
    folder = r"C:\Users\beyba\PycharmProjects\WeatherAPI\Weather json"
    path = os.path.join(folder, "weather.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Weather data saved to: {path}")


@app.get("/api/weather/{city}")
async def weather(city: str, units: str | None = Query(default="metric")):
    normalized_units = units.lower() if units else "metric"

    async with httpx.AsyncClient(timeout=20.0) as client:
        geo_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }
        )

        try:
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                raise HTTPException(status_code=404, detail="City not found")

            location = geo_data["results"][0]
            name = location["name"]
            country = location["country"]
            latitude = location["latitude"]
            longitude = location["longitude"]

        except httpx.HTTPError:
            raise HTTPException(status_code=500, detail="Geocoding API error")

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
            "timezone": "auto"
        }

        weather_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params=weather_params
        )

        try:
            weather_response.raise_for_status()
            weather_data = weather_response.json()

            result = {
                "city": name,
                "country": country,
                "units": normalized_units,
                "current": weather_data["current"]
            }

            weather_json(result)

            return result

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")
