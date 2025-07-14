# IdőKép to Weather Underground

Ez az alkalmazás az [IdőKép](https://www.idokep.hu) oldalról gyűjti az időjárási adatokat, és továbbítja azokat a [Weather Underground](https://www.wunderground.com) szolgáltatásnak.

## Funkciók

- IdőKép oldalról időjárási adatok kinyerése (web scraping)
- IdőKép automata állomások adatainak kinyerése OCR segítségével
- Adatok továbbítása a Weather Underground API-nak
- Konfigurálható időközönkénti adatküldés
- Docker támogatás a könnyű telepítéshez és futtatáshoz

## Telepítés

### Előfeltételek

- Python 3.8+
- Docker (opcionális)

### Telepítés pip segítségével

```bash
git clone https://github.com/amargo/idokep-to-wunderground.git
cd idokep-to-wunderground
pip install -r requirements.txt
```

### Konfiguráció

A program működéséhez szükséges konfigurációs paramétereket környezeti változóként vagy parancssori argumentumként lehet megadni. A környezeti változókat egy `.env` fájlban lehet megadni a következő formátumban:

```
WUNDERGROUND_ID=YOUR_STATION_ID
WUNDERGROUND_KEY=YOUR_API_KEY
IDOKEP_LOCATION=Budapest
SCAN_INTERVAL=900

# Automata scraper konfiguráció (opcionális)
IDOKEP_AUTOMATA_ID=fejnto
USE_AUTOMATA=false
```

### Parancssori argumentumok

Az alkalmazás támogatja a következő parancssori argumentumokat, amelyek felülírják a `.env` fájlban megadott értékeket:

```bash
python src/main.py --once                      # Egyszeri futtatás és kilépés
python src/main.py -o                         # Ugyanaz, mint a --once
python src/main.py --wunderground-id ID       # Weather Underground állomás azonosító
python src/main.py --wunderground-key KEY     # Weather Underground API kulcs
python src/main.py --idokep-location HELY     # IdőKép helyszín (pl. Velence)
python src/main.py --scan-interval 1800       # Lekérdezési időköz másodpercben
python src/main.py --idokep-automata-id ID    # IdőKép automata állomás azonosító
python src/main.py --use-automata             # Automata scraper használata
```

A paraméterek kombinálhatók, például:

```bash
python src/main.py --once --idokep-location Budapest --scan-interval 3600 --idokep-automata-id fejnto --use-automata
```

## IdőKép Automata Scraper használata

Az alkalmazás képes az IdőKép automata állomások adatainak kinyerésére is OCR technológia segítségével. Az automata állomások adatai képként vannak megjelenítve az IdőKép oldalán, ezért az alkalmazás a Tesseract OCR motort használja a képek feldolgozására.

### Használat a fő alkalmazásban

Az automata scraper használatához két mód áll rendelkezésre:

1. **Környezeti változókkal**:
   ```
   IDOKEP_AUTOMATA_ID=fejnto
   USE_AUTOMATA=true
   ```

2. **Parancssori argumentumokkal**:
   ```bash
   python src/main.py --idokep-automata-id fejnto --use-automata
   ```

Az automata scraper használatakor a normál IdőKép scraper helyett az automata scraper fog futási időben kiválasztódni.

### Előfeltételek

Az automata scraper használatához telepíteni kell a Tesseract OCR motort:

#### Windows

1. Töltse le és telepítse a Tesseract OCR-t: https://github.com/UB-Mannheim/tesseract/wiki
2. Adja hozzá a Tesseract telepítési könyvtárát a PATH környezeti változóhoz

#### Linux

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS

```bash
brew install tesseract
```

### Használat példakód

```python
from idokep_automata_scraper import IdokepAutomataScraper

# Automata ID megadása (pl. "fejnto" a Fejér NTO állomáshoz)
scraper = IdokepAutomataScraper("fejnto")

# Adatok lekérése
weather_data = scraper.scrape()

print(f"Hőmérséklet: {weather_data.get('temperature')}°C")
print(f"Harmatpont: {weather_data.get('dew_point')}°C")
print(f"Páratartalom: {weather_data.get('humidity')}%")
print(f"24 órás csapadék: {weather_data.get('precipitation_24h')} mm")
print(f"Csapadékintenzitás: {weather_data.get('precipitation_intensity')} mm/h")
print(f"Mérés ideje: {weather_data.get('measurement_time')}")
```

### Automata állomások azonosítói

Néhány példa automata állomás azonosító:

- `fejnto` - Fejér NTO
- `velence` - Velence
- `budapest` - Budapest

Az azonosítót az IdőKép automata URL-jéből lehet kinyerni: `https://www.idokep.hu/automata/[azonosító]`

## Docker használata

[![Docker Image](https://github.com/amargo/idokep-to-wunderground/actions/workflows/ci.yml/badge.svg)](https://github.com/amargo/idokep-to-wunderground/pkgs/container/idokep-to-wunderground)
[![Docker Hub](https://img.shields.io/docker/v/gszoboszlai/idokep-to-wunderground?label=Docker%20Hub)](https://hub.docker.com/r/gszoboszlai/idokep-to-wunderground)

### Docker image építése

```bash
docker build -t idokep-to-wunderground .
```

### Docker konténer futtatása

```bash
docker run -d --name idokep-to-wunderground --env-file .env idokep-to-wunderground
```

### Docker Compose használata

A projekt tartalmaz egy `docker-compose.yml` fájlt, amely megkönnyíti a konténer kezelését:

```bash
# Konténer indítása
docker-compose up -d

# Konténer leállítása
docker-compose down

# Konténer naplók megtekintése
docker-compose logs -f
```

A Docker Compose automatikusan létrehoz egy `logs` mappát, ahol a naplófájlok tárolódnak, és beállítja a budapesti időzónát.

## Cron használata

Ha inkább cron job-ot szeretne használni az időzített futtatáshoz, adja hozzá a következő sort a crontab-hoz:

```
*/15 * * * * cd /path/to/idokep-to-wunderground && python src/main.py
```

## Licenc

MIT