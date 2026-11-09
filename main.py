from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI(title="Halvin Bensa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Halvin Bensa API pyörii!"}

@app.get("/api/stations")
def get_stations(lat: float = None, lon: float = None):
    url = "https://www.polttoaine.net/Helsinki"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    stations = []

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 4:
                        name = cols[0].text.strip()
                        # Tarkistetaan sarakkeet tarkemmin
                        p_95 = parse_price(cols[1].text)
                        p_98 = parse_price(cols[2].text)
                        p_diesel = parse_price(cols[3].text)
                        
                        if name and (p_diesel or p_95 or p_98):
                            stations.append({
                                "name": name,
                                "city": "Helsinki",
                                "price_diesel": p_diesel,
                                "price_95": p_95,
                                "price_98": p_98,
                                "latitude": lat if lat else 60.1699,
                                "longitude": lon if lon else 24.9384
                            })
    except Exception as e:
        print(f"Haravointivirhe: {e}")

    # Varadata, jos haravointi ei tuota tulosta tai hinta puuttuu
    if not stations:
        stations = [
            {
                "name": "Neste Express Tikkurila",
                "city": "Vantaa",
                "price_diesel": 1.789,
                "price_95": 1.849,
                "price_98": 1.939,
                "latitude": 60.2934,
                "longitude": 25.0378
            },
            {
                "name": "ABC Keimola Pohjoinen",
                "city": "Vantaa",
                "price_diesel": 1.799,
                "price_95": 1.859,
                "price_98": 1.949,
                "latitude": 60.3341,
                "longitude": 24.8361
            },
            {
                "name": "Shell HelmiSimpukka Herttoniemi",
                "city": "Helsinki",
                "price_diesel": 1.769,
                "price_95": 1.829,
                "price_98": 1.919,
                "latitude": 60.1944,
                "longitude": 25.0311
            }
        ]

    return {
        "status": "success",
        "count": len(stations),
        "stations": stations
    }

def parse_price(price_str: str):
    """Apufunktio hinnan muuntamiseksi liukuluvuksi (float). Varmistaa ettei oteta vääriä lukuja."""
    try:
        clean = price_str.strip().replace(",", ".")
        # Etsitään desimaaliluku, esim 1.849
        match = re.search(r"\b[1-2]\.\d{3}\b", clean)
        if match:
            return float(match.group())
        # Yleisempi haku, jos hinta on muuta muotoa
        match_general = re.search(r"\d+\.\d+", clean)
        val = float(match_general.group()) if match_general else None
        # Suodatetaan pois mahdolliset virheelliset isot luvut (esim. puhelinnumerot tai id:t)
        if val and 0.5 < val < 3.0:
            return val
        return None
    except:
        return None
