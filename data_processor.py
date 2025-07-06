import pandas as pd
from config import API_KEYS
import json
import requests
from datetime import datetime
import random

class DataAnalyzer:
    def __init__(self):
        self.openai_api_key = API_KEYS.get('OPENAI')
    
    def process_flight_data(self, raw_data, airport_code):
        """Analyze scraped flight data"""
        if not raw_data:
            return self._generate_empty_analysis()
        
        df = pd.DataFrame(raw_data)
        
        # Clean and process data
        df['time_clean'] = pd.to_datetime(df['time'], format='%H:%M', errors='coerce')
        df['hour'] = df['time_clean'].dt.hour
        
        # Calculate comprehensive metrics
        analysis = {
            'airport_code': airport_code,
            'total_flights': len(df),
            'unique_airlines': len(df['airline'].unique()),
            'unique_origins': len(df['origin'].unique()),
            'busiest_hour': int(df['hour'].mode()[0]) if not df['hour'].empty else 12,
            'airline_distribution': df['airline'].value_counts().head(10).to_dict(),
            'origin_distribution': df['origin'].value_counts().head(10).to_dict(),
            'status_distribution': df['status'].value_counts().to_dict(),
            'hourly_distribution': df['hour'].value_counts().sort_index().to_dict(),
            'sample_flights': df.head(10).to_dict('records'),
            'on_time_percentage': round((df['status'].str.contains('On Time', case=False).sum() / len(df)) * 100, 2),
            'delayed_percentage': round((df['status'].str.contains('Delayed', case=False).sum() / len(df)) * 100, 2),
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return analysis
    
    def generate_insights(self, analysis, aviation_stats=None):
        """Generate insights using AI or rule-based analysis"""
        if self.openai_api_key and self.openai_api_key != 'your-api-key-here':
            return self._generate_ai_insights(analysis, aviation_stats)
        else:
            return self._generate_rule_based_insights(analysis, aviation_stats)
    
    def _generate_ai_insights(self, analysis, aviation_stats):
        """Generate insights using OpenAI API"""
        try:
            prompt = f"""
            Analyze this Australian airport flight data and provide 5 key insights for airline booking market demand:

            Airport: {analysis['airport_code']}
            Total Flights: {analysis['total_flights']}
            Busiest Hour: {analysis['busiest_hour']}:00
            On-time Performance: {analysis['on_time_percentage']}%
            Top Airlines: {list(analysis['airline_distribution'].keys())[:3]}
            Top Origins: {list(analysis['origin_distribution'].keys())[:3]}

            Focus on:
            1. Peak travel demand periods
            2. Airline market share insights
            3. Route popularity trends
            4. Operational efficiency patterns
            5. Market opportunities

            Provide actionable insights for hostel business planning.
            """
            
            # Using requests to call OpenAI API directly
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7,
                'max_tokens': 400
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', 
                                   headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"OpenAI API error: {response.status_code}")
                return self._generate_rule_based_insights(analysis, aviation_stats)
                
        except Exception as e:
            print(f"AI insights generation error: {str(e)}")
            return self._generate_rule_based_insights(analysis, aviation_stats)
    
    def _generate_rule_based_insights(self, analysis, aviation_stats):
        """Generate insights using rule-based analysis"""
        insights = []
        
        # Peak demand analysis
        busiest_hour = analysis['busiest_hour']
        if 6 <= busiest_hour <= 10:
            insights.append(f"🌅 Peak Demand: Morning rush (around {busiest_hour}:00) shows highest flight activity - ideal time for hostel check-ins.")
        elif 15 <= busiest_hour <= 19:
            insights.append(f"🌆 Peak Demand: Afternoon/evening (around {busiest_hour}:00) is busiest - perfect for hostel marketing.")
        else:
            insights.append(f"⏰ Peak Demand: Unusual peak at {busiest_hour}:00 suggests unique travel patterns for this route.")
        
        # Airline market share
        top_airline = list(analysis['airline_distribution'].keys())[0]
        top_airline_share = list(analysis['airline_distribution'].values())[0]
        insights.append(f"✈️ Market Leader: {top_airline} dominates with {top_airline_share} flights ({round(top_airline_share/analysis['total_flights']*100, 1)}% market share).")
        
        # Route popularity
        top_origin = list(analysis['origin_distribution'].keys())[0]
        top_origin_flights = list(analysis['origin_distribution'].values())[0]
        insights.append(f"🗺️ Popular Route: {top_origin} is the top origin with {top_origin_flights} flights - high demand corridor for travelers.")
        
        # Performance insights
        on_time_rate = analysis['on_time_percentage']
        if on_time_rate >= 80:
            insights.append(f"⚡ Excellent Performance: {on_time_rate}% on-time rate indicates reliable service - good for business travelers.")
        elif on_time_rate >= 60:
            insights.append(f"⚠️ Moderate Performance: {on_time_rate}% on-time rate suggests some delays - flexibility needed for hostel bookings.")
        else:
            insights.append(f"🚨 Performance Issues: {on_time_rate}% on-time rate indicates frequent delays - opportunity for extended stays.")
        
        # Market opportunity
        total_flights = analysis['total_flights']
        if total_flights > 20:
            insights.append(f"📈 High Traffic: {total_flights} flights indicate strong market demand - excellent location for hostel business.")
        else:
            insights.append(f"📊 Moderate Traffic: {total_flights} flights suggest steady but manageable demand - good for boutique hostel operations.")
        
        return "\n\n".join(insights)
    
    def _generate_empty_analysis(self):
        """Generate empty analysis structure"""
        return {
            'airport_code': 'N/A',
            'total_flights': 0,
            'unique_airlines': 0,
            'unique_origins': 0,
            'busiest_hour': 12,
            'airline_distribution': {},
            'origin_distribution': {},
            'status_distribution': {},
            'hourly_distribution': {},
            'sample_flights': [],
            'on_time_percentage': 0,
            'delayed_percentage': 0,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
