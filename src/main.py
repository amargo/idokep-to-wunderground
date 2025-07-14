#!/usr/bin/env python3
"""
IdőKép to Weather Underground

Main application that scrapes weather data from IdőKép and sends it to Weather Underground.
"""
import os
import time
import logging
import schedule
from dotenv import load_dotenv

from idokep_scraper import IdokepScraper
from idokep_automata_scraper import IdokepAutomataScraper
from wunderground_client import WundergroundClient

def setup_logging():
    """
    Set up logging configuration with UTF-8 encoding.
    """
    import sys
    import io
    
    # Ensure stdout uses UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create handlers
    handlers = [logging.StreamHandler()]
    
    # Try to add file handler, but continue if it fails
    try:
        import os
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, 'idokep_to_wunderground.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up log file: {e}")
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger()

logger = setup_logging()

def load_config():
    """Load configuration from .env file."""
    load_dotenv()

    config = {
        'wunderground_id': os.getenv('WUNDERGROUND_ID'),
        'wunderground_key': os.getenv('WUNDERGROUND_KEY'),
        'idokep_location': os.getenv('IDOKEP_LOCATION'),
        'idokep_automata_id': os.getenv('IDOKEP_AUTOMATA_ID'),
        'use_automata': os.getenv('USE_AUTOMATA', 'false').lower() == 'true',
        'scan_interval': int(os.getenv('SCAN_INTERVAL', 900))
    }

    # Validate required configuration
    missing_keys = []
    for key in ['wunderground_id', 'wunderground_key']:
        if not config.get(key):
            missing_keys.append(key)
    
    if not config.get('idokep_location') and not (config.get('use_automata') and config.get('idokep_automata_id')):
        missing_keys.append('idokep_location or idokep_automata_id with use_automata=true')

    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

    return config

def update_weather_data():
    """
    Main function to scrape IdőKép and send data to Weather Underground.
    """
    try:
        logger.info("Starting weather data update")

        # Load configuration
        config = load_config()

        # Initialize client
        client = WundergroundClient(config['wunderground_id'], config['wunderground_key'])
        
        # Determine which scraper to use
        weather_data = None
        if config.get('use_automata') and config.get('idokep_automata_id'):
            logger.info(f"Using IdőKép automata scraper with ID: {config['idokep_automata_id']}")
            scraper = IdokepAutomataScraper(config['idokep_automata_id'])
            weather_data = scraper.scrape()
        elif config.get('idokep_location'):
            logger.info(f"Using regular IdőKép scraper with location: {config['idokep_location']}")
            scraper = IdokepScraper(config['idokep_location'])
            weather_data = scraper.scrape()
        else:
            logger.error("No valid scraper configuration found")
            return

        if weather_data:
            # Send data to Weather Underground
            success = client.send_data(weather_data)
            if success:
                logger.info("Weather data successfully updated")
            else:
                logger.error("Failed to send weather data to Weather Underground")
        else:
            logger.error("Failed to scrape weather data from IdőKép")

    except Exception as e:
        logger.exception(f"Error in update_weather_data: {e}")

def run_scheduler(interval):
    """
    Run the scheduler to update weather data at specified intervals.

    Args:
        interval (int): Interval in seconds
    """
    logger.info(f"Starting scheduler with {interval} seconds interval")

    # Schedule the update job
    schedule.every(interval).seconds.do(update_weather_data)

    # Run the update immediately once
    update_weather_data()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_once():
    """Run the update once without scheduling."""
    logger.info("Running one-time update")
    update_weather_data()

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='IdőKép to Weather Underground data bridge')
    parser.add_argument('--once', '-o', action='store_true', help='Run once and exit')
    parser.add_argument('--wunderground-id', help='Weather Underground station ID')
    parser.add_argument('--wunderground-key', help='Weather Underground API key')
    parser.add_argument('--idokep-location', help='IdőKép location (e.g., Velence)')
    parser.add_argument('--idokep-automata-id', help='IdőKép automata ID (e.g., fejnto)')
    parser.add_argument('--use-automata', action='store_true', help='Use IdőKép automata data instead of regular IdőKép data')
    parser.add_argument('--scan-interval', type=int, help='Scan interval in seconds')
    
    return parser.parse_args()

def update_config_from_args(config, args):
    """
    Update configuration with command line arguments if provided.
    
    Args:
        config (dict): Configuration dictionary from .env file
        args (argparse.Namespace): Command line arguments
        
    Returns:
        dict: Updated configuration dictionary
    """
    if args.wunderground_id:
        config['wunderground_id'] = args.wunderground_id
        logger.info(f"Using Weather Underground ID from command line: {args.wunderground_id}")
        
    if args.wunderground_key:
        config['wunderground_key'] = args.wunderground_key
        logger.info("Using Weather Underground API key from command line")
        
    if args.idokep_location:
        config['idokep_location'] = args.idokep_location
        logger.info(f"Using IdőKép location from command line: {args.idokep_location}")
    
    if args.idokep_automata_id:
        config['idokep_automata_id'] = args.idokep_automata_id
        logger.info(f"Using IdőKép automata ID from command line: {args.idokep_automata_id}")
    
    if args.use_automata:
        config['use_automata'] = True
        logger.info("Using IdőKép automata data instead of regular IdőKép data")
        
    if args.scan_interval:
        config['scan_interval'] = args.scan_interval
        logger.info(f"Using scan interval from command line: {args.scan_interval} seconds")
        
    return config

if __name__ == "__main__":
    try:
        import sys
        
        # Parse command line arguments
        args = parse_arguments()
        
        # Load configuration from .env
        config = load_config()
        
        # Update configuration with command line arguments if provided
        config = update_config_from_args(config, args)
        
        # Check if this is a one-time run (via command line arg or env var)
        run_once_mode = args.once or os.getenv('RUN_ONCE', 'false').lower() == 'true'
        
        if run_once_mode:
            logger.info("Running in one-time mode")
            run_once()
        else:
            # Run with scheduler
            run_scheduler(config['scan_interval'])

    except Exception as e:
        logger.exception(f"Application error: {e}")
        exit(1)