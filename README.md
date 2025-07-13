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
WUNDERGROUND_ID=IVELEN71
WUNDERGROUND_KEY=2WdEWdbK
IDOKEP_LOCATION=Velence
SCAN_INTERVAL=900
```

### Futtatás

```bash
python src/main.py
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

## Cron használata

Ha inkább cron job-ot szeretne használni az időzített futtatáshoz, adja hozzá a következő sort a crontab-hoz:

```
*/15 * * * * cd /path/to/idokep-to-wunderground && python src/main.py
```

## Licenc

MIT