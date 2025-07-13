# IdőKép to Weather Underground

Ez az alkalmazás az [IdőKép](https://www.idokep.hu) oldalról gyűjti az időjárási adatokat, és továbbítja azokat a [Weather Underground](https://www.wunderground.com) szolgáltatásnak.

## Funkciók

- IdőKép oldalról időjárási adatok kinyerése (web scraping)
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

Hozzon létre egy `.env` fájlt a következő tartalommal:

```
WUNDERGROUND_ID=TESZT1
WUNDERGROUND_KEY=TEST
IDOKEP_LOCATION=Test
SCAN_INTERVAL=900
```

### Futtatás

```bash
python src/main.py
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
```

A paraméterek kombinálhatók, például:

```bash
python src/main.py --once --idokep-location Budapest --scan-interval 3600
```

## Docker használata

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