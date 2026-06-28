from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import Config
from weather_client import fetch_weather
from cache import cache

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Weather API", description="API de clima usando Open-Meteo")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Validar configuración (aunque no tenemos API key)
Config.validate()

@app.get("/weather")
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE}/minute")
async def get_weather(
    request: Request,
    city: str = Query(..., description="Nombre de la ciudad (ej. Madrid, Buenos Aires)")
):
    """
    Devuelve el clima actual para la ciudad especificada.
    Utiliza caché de 12 horas para evitar llamadas repetidas a la API externa.
    """
    # Normalizar clave para caché
    cache_key = city.strip().lower()

    # 1. Intentar obtener del caché
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return JSONResponse(content=cached_data)

    # 2. Llamar a la API externa
    try:
        weather_data = await fetch_weather(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # Cualquier otro error
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    # 3. Guardar en caché
    cache.set(cache_key, weather_data)

    return JSONResponse(content=weather_data)

# Manejador de excepciones global para errores inesperados
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno. Intente más tarde."}
    )

# Para ejecutar directamente con uvicorn (opcional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)