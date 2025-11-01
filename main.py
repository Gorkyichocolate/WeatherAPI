from fastapi import FastAPI, HTTPException, Query
import httpx
from producer import send_to_queue
app = FastAPI()

@app.get("/api/weather/{city}")
async def weather(city: str, units: str | None = Query(default="metric")):
    normalized_units = units.lower() if units else "metric"

    async with httpx.AsyncClient(timeout=2.0) as client:
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
            send_to_queue(result)
            return result

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")