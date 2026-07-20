"""
IdőKép Scraper Module

This module is responsible for scraping weather data from IdőKép website.
"""
import logging
import re
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class IdokepScraper:
    """Class for scraping weather data from IdőKép website."""
    
    BASE_URL = "https://www.idokep.hu/idojaras"
    
    def __init__(self, location):
        """
        Initialize the IdőKép scraper.
        
        Args:
            location (str): The location to get weather data for (e.g., 'Velence')
        """
        self.location = location.strip()
        self.url = f"{self.BASE_URL}/{quote(self.location, safe='')}"
        
    def _extract_temperature(self, soup):
        """
        Extract the current temperature from the page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            float: Temperature in Celsius or None if not found
        """
        temp_element = soup.select_one('.current-temperature')
        if not temp_element:
            return None
            
        temp_text = temp_element.get_text(" ", strip=True)
        try:
            # Időkép currently uses ℃, but older pages used °C or ˚C.
            match = re.search(r"[-+]?\d+(?:[.,]\d+)?", temp_text)
            if not match:
                raise ValueError
            temperature = float(match.group(0).replace(',', '.'))
            logger.info(f"Found temperature: {temperature}°C")
            return temperature
        except ValueError:
            logger.error(f"Could not parse temperature from: {temp_text}")
            return None
    
    def _extract_lake_temperature(self, soup):
        """
        Extract the lake temperature if available.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            float: Lake temperature in Celsius or None if not found
        """
        lake_temp_text = soup.find(string=lambda text: 'Velencei-tó:' in text if text else False)
        if not lake_temp_text:
            return None
            
        try:
            match = re.search(r"[-+]?\d+(?:[.,]\d+)?", lake_temp_text)
            if match:
                lake_temp = float(match.group(0).replace(',', '.'))
                logger.info(f"Found lake temperature: {lake_temp}°C")
                return lake_temp
        except ValueError:
            logger.error(f"Could not parse lake temperature from: {lake_temp_text}")
        return None
    
    def _extract_condition(self, soup):
        """
        Extract the current weather condition.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Weather condition or None if not found
        """
        condition_element = soup.select_one('.current-weather')
        if condition_element:
            condition = condition_element.text.strip()
            logger.info(f"Found weather condition: {condition}")
            return condition
        return None
    
    def _extract_alert(self, soup):
        """
        Extract weather alert if available.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Weather alert or None if not found
        """
        alert_element = soup.select_one('#topalertbar > a:nth-child(1)')
        if alert_element:
            alert = alert_element.text.strip()
            logger.info(f"Found weather alert: {alert}")
            return alert
        return None
    
    def scrape(self):
        """
        Scrape weather data from IdőKép.
        
        Returns:
            dict: Weather data including temperature, humidity, etc.
        """
        try:
            logger.info(f"Scraping data from {self.url}")
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract data using helper methods
            temperature = self._extract_temperature(soup)
            lake_temp = self._extract_lake_temperature(soup)
            condition = self._extract_condition(soup)
            alert = self._extract_alert(soup)
            # The regular page does not expose measured relative humidity.
            humidity = None
            
            # Create weather data dictionary
            weather_data = {
                'temperature': temperature,
                'lake_temperature': lake_temp,
                'humidity': humidity,
                'wind_speed': None,  # No wind data available
                'wind_direction': None,  # No wind direction available
                'pressure': None,  # No pressure data available
                'precipitation': None,  # Do not invent a rainfall measurement
                'condition': condition,
                'alert': alert
            }
            
            logger.info(f"Successfully scraped data: {weather_data}")
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data from IdőKép: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing IdőKép data: {e}")
            return None
