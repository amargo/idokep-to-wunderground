import sys
import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

sys.path.insert(0, "src")

from idokep_scraper import IdokepScraper
from idokep_automata_scraper import IdokepAutomataScraper
from wunderground_client import WundergroundClient


class ScraperTests(unittest.TestCase):
    def test_regular_scraper_parses_current_idokep_temperature_format(self):
        scraper = IdokepScraper("Budapest")
        self.assertEqual(scraper._extract_temperature(BeautifulSoup(
            "<div class='current-temperature'>26℃</div>", "html.parser"
        )), 26.0)

    def test_automata_numeric_ranges_reject_invalid_ocr(self):
        self.assertEqual(IdokepAutomataScraper._valid_value("humidity", 55), 55)
        self.assertIsNone(IdokepAutomataScraper._valid_value("humidity", 155))


class WundergroundClientTests(unittest.TestCase):
    def setUp(self):
        self.client = WundergroundClient("TEST", "KEY")

    def test_converts_automata_measurements(self):
        converted = self.client._convert_to_wunderground_format({
            "temperature": 20,
            "dew_point": 10,
            "humidity": 50,
            "precipitation_intensity": 2.54,
            "precipitation_24h": 25.4,
        })
        self.assertEqual(converted["tempf"], 68.0)
        self.assertEqual(converted["dewptf"], 50.0)
        self.assertAlmostEqual(converted["rainin"], 0.1, places=5)
        self.assertAlmostEqual(converted["dailyrainin"], 1.0, places=5)

    def test_does_not_send_fabricated_rainfall(self):
        converted = self.client._convert_to_wunderground_format({"temperature": 20})
        self.assertNotIn("rainin", converted)

    @patch("wunderground_client.requests.get")
    def test_accepts_only_exact_success_response(self, get):
        response = Mock(status_code=200, text="success\n")
        get.return_value = response
        self.assertTrue(self.client.send_data({"temperature": 20}))


if __name__ == "__main__":
    unittest.main()
