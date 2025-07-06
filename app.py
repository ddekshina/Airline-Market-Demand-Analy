from flask import Flask, render_template, request, jsonify
from scraper import FlightScraper, AviationDataAPI
from data_processor import DataAnalyzer
import json
import os

app = Flask(__name__)
scraper = FlightScraper()
analyzer = DataAnalyzer()
aviation_api = AviationDataAPI()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        airport = request.form.get('airport', 'SYD')
        
        try:
            # Scrape real flight data
            print(f"Scraping data for airport: {airport}")
            flight_data = scraper.scrape_airport_flights(airport)
            
            if not flight_data:
                return render_template('index.html', error="Failed to scrape flight data. Please try again.")
            
            # Get additional aviation data
            aviation_stats = aviation_api.get_flight_stats(airport)
            
            # Analyze data
            analysis = analyzer.process_flight_data(flight_data, airport)
            insights = analyzer.generate_insights(analysis, aviation_stats)
            
            return render_template('results.html',
                               flights=flight_data[:15],  # Show top 15 flights
                               analysis=analysis,
                               insights=insights,
                               airport=airport,
                               aviation_stats=aviation_stats)
        
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return render_template('index.html', error=f"An error occurred: {str(e)}")
    
    return render_template('index.html')

@app.route('/api/flights/<airport>')
def api_flights(airport):
    """API endpoint for getting flight data"""
    try:
        flight_data = scraper.scrape_airport_flights(airport)
        return jsonify(flight_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)