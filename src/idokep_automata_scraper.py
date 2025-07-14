#!/usr/bin/env python3
"""
IdőKép Automata Scraper

Scrapes weather data from IdőKép automata pages.
"""
import re
import base64
import logging
import requests
import os
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract

# Tesseract konfigurálása Docker környezethez
if os.path.exists('/usr/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

logger = logging.getLogger(__name__)

class IdokepAutomataScraper:
    """
    Scraper for IdőKép automata pages.
    """
    
    def __init__(self, automata_id):
        """
        Initialize the scraper with the automata ID.
        
        Args:
            automata_id (str): The ID of the automata (e.g., 'fejnto' for Fejér NTO)
        """
        self.automata_id = automata_id
        self.base_url = f"https://www.idokep.hu/automata/{automata_id}"
        
    def _get_page_content(self):
        """
        Get the HTML content of the automata page.
        
        Returns:
            BeautifulSoup: Parsed HTML content
        """
        try:
            logger.info(f"Fetching automata data from {self.base_url}")
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching automata page: {e}")
            return None
    
    def _extract_image_data(self, img_tag):
        """
        Extract and decode base64 image data from an img tag.
        
        Args:
            img_tag: BeautifulSoup img tag
            
        Returns:
            PIL.Image: Decoded image
        """
        try:
            if not img_tag or not img_tag.get('src'):
                return None
                
            # Extract base64 data
            src = img_tag['src']
            base64_data = re.sub(r'^data:image/\w+;base64,', '', src)
            
            # Decode base64 to image
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            
            # Return the image for OCR processing
            return image
        except Exception as e:
            logger.error(f"Error extracting image data: {e}")
            return None
    
    def _process_image_with_ocr(self, image):
        """
        Process image with OCR to extract text.
        
        Args:
            image: PIL.Image object
            
        Returns:
            str: Extracted text
        """
        try:
            if not image:
                return None
                
            # Process with pytesseract
            # Using a simple configuration for numeric data
            text = pytesseract.image_to_string(
                image, 
                config='--psm 7 --oem 3 -c tessedit_char_whitelist="0123456789,.-"'
            )
            
            # Clean up the text
            text = text.strip()
            
            return text
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return None
    
    def _extract_numeric_value(self, text):
        """
        Extract numeric value from OCR text.
        
        Args:
            text (str): OCR extracted text
            
        Returns:
            float or None: Extracted numeric value
        """
        if not text:
            return None
            
        try:
            # Replace comma with dot for decimal point
            text = text.replace(',', '.')
            
            # Find all numbers in the text
            matches = re.findall(r'-?\d+\.?\d*', text)
            if matches:
                return float(matches[0])
            
            return None
        except Exception as e:
            logger.error(f"Error extracting numeric value: {e}")
            return None
    
    def _extract_measurement_time(self, soup):
        """
        Extract the measurement time from the page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            str: Measurement time
        """
        try:
            time_tag = soup.select_one('time')
            if time_tag and time_tag.get('datetime'):
                return time_tag['datetime']
            return None
        except Exception as e:
            logger.error(f"Error extracting measurement time: {e}")
            return None
    
    def scrape(self):
        """
        Scrape weather data from the automata page.
        
        Returns:
            dict: Weather data
        """
        soup = self._get_page_content()
        if not soup:
            logger.error("Failed to get automata page content")
            return None
        
        # Initialize weather data dictionary
        weather_data = {
            'temperature': None,
            'dew_point': None,
            'humidity': None,
            'precipitation_24h': None,
            'precipitation_intensity': None,
            'measurement_time': None
        }
        
        # Extract measurement time
        weather_data['measurement_time'] = self._extract_measurement_time(soup)
        
        # Find all table rows
        rows = soup.select('table.table tr')
        
        for row in rows:
            # Get the header and data cell
            header = row.select_one('th')
            data_cell = row.select_one('td')
            
            if not header or not data_cell:
                continue
                
            header_text = header.text.strip()
            
            # Extract image tag
            img_tag = data_cell.select_one('img')
            
            if img_tag:
                # Process the image
                image = self._extract_image_data(img_tag)
                ocr_text = self._process_image_with_ocr(image)
                value = self._extract_numeric_value(ocr_text)
                
                # Map to the appropriate field based on header
                if "Hőmérséklet" in header_text:
                    weather_data['temperature'] = value
                elif "Harmatpont" in header_text:
                    weather_data['dew_point'] = value
                elif "Páratartalom" in header_text:
                    weather_data['humidity'] = value
                elif "24 órás csapadék" in header_text:
                    weather_data['precipitation_24h'] = value
                elif "Csapadékintenzitás" in header_text:
                    weather_data['precipitation_intensity'] = value
        
        logger.info(f"Scraped automata data: {weather_data}")
        return weather_data


# Example usage
if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Create scraper for Fejér NTO automata
    scraper = IdokepAutomataScraper("fejnto")
    
    # Scrape data
    data = scraper.scrape()
    
    # Print results
    print(f"Temperature: {data.get('temperature')}°C")
    print(f"Dew Point: {data.get('dew_point')}°C")
    print(f"Humidity: {data.get('humidity')}%")
    print(f"24h Precipitation: {data.get('precipitation_24h')} mm")
    print(f"Precipitation Intensity: {data.get('precipitation_intensity')} mm/h")
    print(f"Measurement Time: {data.get('measurement_time')}")
