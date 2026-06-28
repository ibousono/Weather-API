I used https://open-meteo.com for the API

steps:

python3 -m venv venv
source venv/bin/activate   # o venv\Scripts\activate en Windows

pip install fastapi uvicorn[standard] httpx python-dotenv slowapi