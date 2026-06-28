# Weather API

A simple weather API that fetches current weather data from [Open-Meteo](https://open-meteo.com/).

> This is a solution for the [Weather API project](https://roadmap.sh/projects/weather-api-wrapper-service) on roadmap.sh

## Features

- Get current weather by city name
- In-memory caching with TTL (12 hours)
- Rate limiting (10 requests per minute)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/weather-api.git
cd weather-api

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, uses in-memory cache by default)
cp .env.example .env

# Run the server
python3 main.py

# On another terminal run for example: 
curl "http://localhost:8000/weather?city=Madrid"

# Response example
{
  "city": "Madrid",
  "country": "España",
  "temperature": 23.5,
  "feels_like": 23.5,
  "humidity": 55,
  "wind_speed": 8.4,
  "conditions": "Clear",
  "weather_code": 0,
  "time": "2026-06-29T01:45"
}
