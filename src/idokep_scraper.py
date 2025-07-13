"""
IdőKép Scraper Module

This module is responsible for scraping weather data from IdőKép website.
"""
import logging
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
        self.location = location
        self.url = f"{self.BASE_URL}/{location}"
        
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
            
        temp_text = temp_element.text.strip()
        try:
            # Remove the degree symbol and convert to float
            temperature = float(temp_text.replace('˚C', '').strip())
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
            lake_temp_parts = lake_temp_text.strip().split(':')
            if len(lake_temp_parts) > 1:
                lake_temp = float(lake_temp_parts[1].replace('°C', '').strip())
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
    
    def _estimate_humidity(self, condition):
        """
        Estimate humidity based on weather condition.
        
        Args:
            condition (str): Weather condition text
            
        Returns:
            int: Estimated humidity percentage or None
        """
        if not condition:
            return None
            
        if 'eső' in condition.lower() or 'zivatar' in condition.lower():
            return 80  # Estimate high humidity during rain/storms
        elif 'felhős' in condition.lower():
            return 60  # Estimate moderate humidity when cloudy
        elif 'napos' in condition.lower():
            return 40  # Estimate lower humidity when sunny
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
            humidity = self._estimate_humidity(condition)
            
            # Create weather data dictionary
            weather_data = {
                'temperature': temperature,
                'lake_temperature': lake_temp,
                'humidity': humidity,
                'wind_speed': None,  # No wind data available
                'wind_direction': None,  # No wind direction available
                'pressure': None,  # No pressure data available
                'precipitation': 0.0,  # Default to 0 if no precipitation data
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