"""
Weather Underground API Client

This module handles sending weather data to the Weather Underground PWS API.
"""
import logging
import requests

logger = logging.getLogger(__name__)

class WundergroundClient:
    """Client for submitting data to Weather Underground Personal Weather Station API."""
    
    BASE_URL = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
    
    def __init__(self, station_id, api_key):
        """
        Initialize the Weather Underground client.
        
        Args:
            station_id (str): The Weather Underground station ID
            api_key (str): The Weather Underground API key
        """
        self.station_id = station_id
        self.api_key = api_key
        
    def send_data(self, weather_data):
        """
        Send weather data to Weather Underground.
        
        Args:
            weather_data (dict): Weather data including temperature, humidity, etc.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not weather_data:
            logger.error("No weather data to send")
            return False
            
        # Convert IdőKép data format to Weather Underground format
        wu_data = self._convert_to_wunderground_format(weather_data)
        
        # Add authentication parameters
        params = {
            'ID': self.station_id,
            'PASSWORD': self.api_key,
            'action': 'updateraw',
            'dateutc': 'now',
        }
        
        # Merge with weather data
        params.update(wu_data)
        
        try:
            logger.info(f"Sending data to Weather Underground for station {self.station_id}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200 and "success" in response.text.lower():
                logger.info("Data successfully sent to Weather Underground")
                return True
            else:
                logger.error(f"Failed to send data: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error sending data to Weather Underground: {e}")
            return False
    
    def _convert_to_wunderground_format(self, weather_data):
        """
        Convert IdőKép data format to Weather Underground format.
        
        Args:
            weather_data (dict): Weather data from IdőKép
            
        Returns:
            dict: Weather data in Weather Underground format
        """
        wu_data = {}
        
        # Temperature in Celsius - prefer air temperature, fallback to lake temperature if needed
        if weather_data.get('temperature') is not None:
            wu_data['tempf'] = self._celsius_to_fahrenheit(weather_data['temperature'])
            wu_data['tempc'] = weather_data['temperature']
        elif weather_data.get('lake_temperature') is not None:
            # If we only have lake temperature, use that as a fallback
            wu_data['tempf'] = self._celsius_to_fahrenheit(weather_data['lake_temperature'])
            wu_data['tempc'] = weather_data['lake_temperature']
            logger.info(f"Using lake temperature as fallback: {weather_data['lake_temperature']}°C")
        
        # Humidity
        if weather_data.get('humidity') is not None:
            wu_data['humidity'] = weather_data['humidity']
        
        # Barometric pressure in hPa
        if weather_data.get('pressure') is not None:
            wu_data['baromin'] = self._hpa_to_inches(weather_data['pressure'])
        
        # Wind speed in km/h
        if weather_data.get('wind_speed') is not None:
            wu_data['windspeedmph'] = self._kmh_to_mph(weather_data['wind_speed'])
        
        # Wind direction
        if weather_data.get('wind_direction') is not None:
            wu_data['winddir'] = self._convert_wind_direction(weather_data['wind_direction'])
        
        # Precipitation in mm
        if weather_data.get('precipitation') is not None:
            wu_data['rainin'] = self._mm_to_inches(weather_data['precipitation'])
        
        # Weather condition as a string
        if weather_data.get('condition') is not None:
            wu_data['weather'] = weather_data['condition']
            
        # Weather alert if available
        if weather_data.get('alert') is not None:
            wu_data['weatherAlert'] = weather_data['alert']
            logger.info(f"Weather alert: {weather_data['alert']}")

        
        return wu_data
    
    @staticmethod
    def _celsius_to_fahrenheit(celsius):
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32
    
    @staticmethod
    def _hpa_to_inches(hpa):
        """Convert hectopascals (hPa) to inches of mercury."""
        return hpa * 0.02953
    
    @staticmethod
    def _kmh_to_mph(kmh):
        """Convert kilometers per hour to miles per hour."""
        return kmh * 0.621371
    
    @staticmethod
    def _mm_to_inches(mm):
        """Convert millimeters to inches."""
        return mm * 0.0393701
    
    @staticmethod
    def _convert_wind_direction(direction):
        """
        Convert wind direction from text (e.g., 'ÉNy') to degrees.
        
        Args:
            direction (str): Wind direction in Hungarian abbreviation
            
        Returns:
            int: Wind direction in degrees
        """
        # Hungarian wind direction abbreviations to degrees
        direction_map = {
            'É': 0,    # North
            'ÉK': 45,  # Northeast
            'K': 90,   # East
            'DK': 135, # Southeast
            'D': 180,  # South
            'DNy': 225, # Southwest
            'Ny': 270, # West
            'ÉNy': 315 # Northwest
        }
        
        return direction_map.get(direction, 0)  # Default to North if unknown