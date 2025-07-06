import pandas as pd
from config import API_KEYS
import openai
import json

openai.api_key = API_KEYS['OPENAI']

class DataAnalyzer:
    def process_flight_data(self, raw_data):
        """Analyze scraped flight data"""
        df = pd.DataFrame(raw_data)
        
        # Extract hour from time
        df['hour'] = pd.to_datetime(df['time']).dt.hour
        
        # Calculate metrics
        analysis = {
            'total_flights': len(df),
            'busiest_hour': df['hour'].mode()[0],
            'airline_distribution': df['airline'].value_counts().to_dict(),
            'status_distribution': df['status'].value_counts().to_dict(),
            'sample_data': df.head(5).to_dict('records')
        }
        
        return analysis
    
    def generate_insights(self, analysis):
        """Use AI to generate insights"""
        prompt = f"""
        Analyze this Australian flight data and provide 5 key insights:
        {json.dumps(analysis, indent=2)}
        
        Focus on:
        - Peak travel times
        - Airline market share
        - Flight status trends
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=256
        )
        
        return response.choices[0].message['content']