from flask import Flask, render_template, request
from scraper import LegalScraper, AviationData
from data_processor import DataAnalyzer
import json

app = Flask(__name__)
scraper = LegalScraper()
analyzer = DataAnalyzer()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        airport = request.form.get('airport', 'SYD')
        
        # Scrape real data
        flight_data = scraper.scrape_airport_flights(airport)
        govt_data = AviationData().get_bitre_stats()
        
        # Analyze data
        analysis = analyzer.process_flight_data(flight_data)
        insights = analyzer.generate_insights(analysis)
        
        return render_template('results.html',
                           flights=flight_data[:10],
                           analysis=analysis,
                           insights=insights,
                           airport=airport)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)