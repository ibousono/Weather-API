import httpx
from config import Config

async def geocode_city(city: str):
    """
    Convierte nombre de ciudad a coordenadas usando Open-Meteo Geocoding API.
    Retorna un dict con latitud, longitud, nombre y país.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "es",
        "format": "json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise ValueError(f"No se pudo geocodificar la ciudad '{city}' (código {response.status_code})")
        except httpx.TimeoutException:
            raise RuntimeError("El servicio de geocodificación tardó demasiado")

        data = response.json()
        results = data.get("results", [])
        if not results:
            raise ValueError(f"Ciudad '{city}' no encontrada")

        first = results[0]
        return {
            "latitude": first["latitude"],
            "longitude": first["longitude"],
            "name": first.get("name", city),
            "country": first.get("country", "")
        }

async def fetch_weather(city: str):
    """
    Obtiene el clima actual para una ciudad usando Open-Meteo.
    Retorna un dict con los datos relevantes.
    """
    # 1. Geocodificar
    location = await geocode_city(city)

    # 2. Llamar a la API de pronóstico
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
                    "weather_code", "apparent_temperature"],
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
        "forecast_days": 1
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Error en API de Open-Meteo: {e.response.status_code}")
        except httpx.TimeoutException:
            raise RuntimeError("La API de Open-Meteo tardó demasiado")

        data = response.json()
        current = data.get("current", {})

        # Mapeo de códigos de clima a descripciones en español
        weather_codes = {
            0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
            3: "Nublado", 45: "Niebla", 48: "Niebla con escarcha",
            51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna intensa",
            56: "Llovizna helada ligera", 57: "Llovizna helada intensa",
            61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa",
            66: "Lluvia helada ligera", 67: "Lluvia helada intensa",
            71: "Nevada ligera", 73: "Nevada moderada", 75: "Nevada intensa",
            77: "Granizo", 80: "Chubascos ligeros", 81: "Chubascos moderados",
            82: "Chubascos intensos", 85: "Nevada ligera", 86: "Nevada intensa",
            95: "Tormenta", 96: "Tormenta con granizo ligero", 99: "Tormenta con granizo intenso"
        }
        weather_code = current.get("weather_code")
        condition = weather_codes.get(weather_code, "Desconocido")

        return {
            "city": location["name"],
            "country": location["country"],
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "conditions": condition,
            "weather_code": weather_code,
            "time": current.get("time")
        }