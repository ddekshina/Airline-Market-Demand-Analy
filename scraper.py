import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
from config import SCRAPING_CONFIG
import random

class LegalScraper:
    def __init__(self):
        self.headers = {'User-Agent': SCRAPING_CONFIG['USER_AGENT']}
        self.delay = SCRAPING_CONFIG['REQUEST_DELAY']
        
    def scrape_airport_flights(self, airport_code):
        """Scrape real flight data from airport website"""
        base_url = self._get_airport_url(airport_code)
        
        try:
            time.sleep(self.delay)  # Respectful delay
            response = requests.get(base_url, headers=self.headers, timeout=SCRAPING_CONFIG['TIMEOUT'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            flights = []
            
            # Extract flight data (specific selectors may need adjustment)
            for row in soup.select('.flight-row:not(.header)'):
                flight = {
                    'time': self._clean_text(row.select_one('.time').text),
                    'flight': self._clean_text(row.select_one('.flight-number').text),
                    'origin': self._clean_text(row.select_one('.origin-destination').text),
                    'airline': self._clean_text(row.select_one('.airline').text),
                    'status': self._clean_text(row.select_one('.status').text),
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                flights.append(flight)
                
            return flights
            
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            return None

    def _get_airport_url(self, code):
        """Get the correct URL for each airport"""
        urls = {
            'SYD': 'https://www.sydneyairport.com.au/flights?query=arrivals',
            'MEL': 'https://www.melbourneairport.com.au/flights/arrivals',
            'BNE': 'https://www.bne.com.au/flight-information/arrivals'
        }
        return urls.get(code, urls['SYD'])  # Default to SYD

    def _clean_text(self, text):
        """Clean scraped text data"""
        return text.strip().replace('\n', '').replace('\t', '')

class AviationData:
    def get_bitre_stats(self):
        """Get official Australian aviation statistics"""
        url = "https://www.bitre.gov.au/publications/ongoing/airport_traffic_data.csv"
        try:
            df = pd.read_csv(url)
            return df[df['YearMonth'].str.contains('2023')].to_dict('records')
        except:
            return None