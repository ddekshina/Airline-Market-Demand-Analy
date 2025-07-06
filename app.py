#!/usr/bin/env python3
"""
Airline Market Demand Analyzer
A comprehensive web application for analyzing airline booking trends for hostel groups in Australia
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import numpy as np
from collections import defaultdict, Counter
import time
import random

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = 'airline_data.db'
    
    # Free API Keys (Set these as environment variables)
    AVIATIONSTACK_API_KEY = os.environ.get('AVIATIONSTACK_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Australian airports focus
    MAJOR_AIRPORTS = {
        'SYD': 'Sydney',
        'MEL': 'Melbourne', 
        'BNE': 'Brisbane',
        'PER': 'Perth',
        'ADL': 'Adelaide',
        'CNS': 'Cairns',
        'DRW': 'Darwin',
        'HBA': 'Hobart'
    }

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Database initialization
def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(Config.DATABASE_URL)
    cursor = conn.cursor()
    
    # Flight data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT,
            departure_airport TEXT,
            arrival_airport TEXT,
            departure_city TEXT,
            arrival_city TEXT,
            departure_date TEXT,
            arrival_date TEXT,
            airline TEXT,
            aircraft_type TEXT,
            status TEXT,
            price_estimate REAL,
            demand_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Market trends table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT,
            date TEXT,
            demand_level TEXT,
            avg_price REAL,
            flight_count INTEGER,
            popularity_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Data Collection Module
class AirlineDataCollector:
    def __init__(self):
        self.aviationstack_key = Config.AVIATIONSTACK_API_KEY
        self.base_url = "http://api.aviationstack.com/v1"
        
    def get_flight_data(self, limit=100):
        """Fetch real flight data from AviationStack API"""
        flights = []
        
        try:
            # Get live flights data
            url = f"{self.base_url}/flights"
            params = {
                'access_key': self.aviationstack_key,
                'limit': limit,
                'flight_status': 'active'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for flight in data['data']:
                        flights.append(self._parse_flight_data(flight))
            else:
                print(f"API Error: {response.status_code}")
                # Fallback to synthetic data
                flights = self._generate_synthetic_data(limit)
                
        except Exception as e:
            print(f"Error fetching flight data: {e}")
            # Generate synthetic data as fallback
            flights = self._generate_synthetic_data(limit)
            
        return flights
    
    def _parse_flight_data(self, flight_data):
        """Parse flight data from API response"""
        departure = flight_data.get('departure', {})
        arrival = flight_data.get('arrival', {})
        
        return {
            'flight_number': flight_data.get('flight', {}).get('number', 'Unknown'),
            'departure_airport': departure.get('iata', ''),
            'arrival_airport': arrival.get('iata', ''),
            'departure_city': departure.get('timezone', '').split('/')[-1] if departure.get('timezone') else '',
            'arrival_city': arrival.get('timezone', '').split('/')[-1] if arrival.get('timezone') else '',
            'departure_date': departure.get('scheduled', ''),
            'arrival_date': arrival.get('scheduled', ''),
            'airline': flight_data.get('airline', {}).get('name', 'Unknown'),
            'aircraft_type': flight_data.get('aircraft', {}).get('registration', 'Unknown'),
            'status': flight_data.get('flight_status', 'unknown'),
            'price_estimate': random.randint(200, 1500),  # Synthetic pricing
            'demand_score': random.randint(1, 10)
        }
    
    def _generate_synthetic_data(self, count=100):
        """Generate synthetic flight data for demo purposes"""
        flights = []
        airlines = ['Qantas', 'Virgin Australia', 'Jetstar', 'Tigerair', 'Rex Airlines']
        statuses = ['active', 'scheduled', 'landed', 'cancelled', 'delayed']
        
        for i in range(count):
            dep_airport = random.choice(list(Config.MAJOR_AIRPORTS.keys()))
            arr_airport = random.choice(list(Config.MAJOR_AIRPORTS.keys()))
            
            # Ensure different airports
            while arr_airport == dep_airport:
                arr_airport = random.choice(list(Config.MAJOR_AIRPORTS.keys()))
            
            # Generate date within last 30 days
            date_offset = random.randint(0, 30)
            flight_date = datetime.now() - timedelta(days=date_offset)
            
            flights.append({
                'flight_number': f"{random.choice(['QF', 'VA', 'JQ', 'TT', 'ZL'])}{random.randint(100, 999)}",
                'departure_airport': dep_airport,
                'arrival_airport': arr_airport,
                'departure_city': Config.MAJOR_AIRPORTS[dep_airport],
                'arrival_city': Config.MAJOR_AIRPORTS[arr_airport],
                'departure_date': flight_date.strftime('%Y-%m-%d %H:%M:%S'),
                'arrival_date': (flight_date + timedelta(hours=random.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S'),
                'airline': random.choice(airlines),
                'aircraft_type': f"Boeing {random.choice(['737', '787', '777'])}",
                'status': random.choice(statuses),
                'price_estimate': random.randint(150, 1200),
                'demand_score': random.randint(1, 10)
            })
        
        return flights

# Data Processing Module
class TrendAnalyzer:
    def __init__(self):
        self.db_path = Config.DATABASE_URL
        
    def store_flight_data(self, flights):
        """Store flight data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for flight in flights:
            cursor.execute('''
                INSERT OR REPLACE INTO flights 
                (flight_number, departure_airport, arrival_airport, departure_city, arrival_city,
                 departure_date, arrival_date, airline, aircraft_type, status, price_estimate, demand_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flight['flight_number'], flight['departure_airport'], flight['arrival_airport'],
                flight['departure_city'], flight['arrival_city'], flight['departure_date'],
                flight['arrival_date'], flight['airline'], flight['aircraft_type'],
                flight['status'], flight['price_estimate'], flight['demand_score']
            ))
        
        conn.commit()
        conn.close()
    
    def get_popular_routes(self, limit=10):
        """Analyze most popular routes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                departure_airport || ' → ' || arrival_airport as route,
                departure_city || ' → ' || arrival_city as cities,
                COUNT(*) as flight_count,
                AVG(price_estimate) as avg_price,
                AVG(demand_score) as avg_demand
            FROM flights 
            WHERE status IN ('active', 'scheduled', 'landed')
            GROUP BY departure_airport, arrival_airport
            ORDER BY flight_count DESC, avg_demand DESC
            LIMIT ?
        ''', (limit,))
        
        routes = cursor.fetchall()
        conn.close()
        
        return [{
            'route': route[0],
            'cities': route[1],
            'flight_count': route[2],
            'avg_price': round(route[3], 2),
            'avg_demand': round(route[4], 2)
        } for route in routes]
    
    def get_price_trends(self):
        """Analyze price trends over time"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT 
                DATE(departure_date) as date,
                departure_airport || ' → ' || arrival_airport as route,
                AVG(price_estimate) as avg_price,
                COUNT(*) as flight_count
            FROM flights 
            WHERE departure_date IS NOT NULL
            GROUP BY DATE(departure_date), route
            ORDER BY date DESC
        ''', conn)
        conn.close()
        
        return df
    
    def get_demand_analysis(self):
        """Analyze demand patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # High demand periods
        cursor.execute('''
            SELECT 
                DATE(departure_date) as date,
                AVG(demand_score) as avg_demand,
                COUNT(*) as flight_count
            FROM flights 
            WHERE departure_date IS NOT NULL
            GROUP BY DATE(departure_date)
            HAVING COUNT(*) > 5
            ORDER BY avg_demand DESC
            LIMIT 10
        ''')
        
        high_demand_periods = cursor.fetchall()
        
        # Popular destinations
        cursor.execute('''
            SELECT 
                arrival_city,
                COUNT(*) as arrival_count,
                AVG(demand_score) as avg_demand,
                AVG(price_estimate) as avg_price
            FROM flights 
            WHERE arrival_city IS NOT NULL AND arrival_city != ''
            GROUP BY arrival_city
            ORDER BY arrival_count DESC, avg_demand DESC
            LIMIT 10
        ''')
        
        popular_destinations = cursor.fetchall()
        
        conn.close()
        
        return {
            'high_demand_periods': [{
                'date': period[0],
                'avg_demand': round(period[1], 2),
                'flight_count': period[2]
            } for period in high_demand_periods],
            'popular_destinations': [{
                'destination': dest[0],
                'arrival_count': dest[1],
                'avg_demand': round(dest[2], 2),
                'avg_price': round(dest[3], 2)
            } for dest in popular_destinations]
        }

# AI Integration Module
class AIInsightGenerator:
    def __init__(self):
        self.openai_key = Config.OPENAI_API_KEY
        
    def generate_market_insights(self, trend_data):
        """Generate AI insights about market trends"""
        if not self.openai_key:
            return self._generate_synthetic_insights(trend_data)
        
        try:
            # Prepare data summary for AI
            summary = self._prepare_data_summary(trend_data)
            
            headers = {
                'Authorization': f'Bearer {self.openai_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a travel industry analyst specializing in Australian airline market trends for hostel businesses.'
                    },
                    {
                        'role': 'user',
                        'content': f'Analyze these airline booking trends and provide insights for hostel operators in Australia: {summary}'
                    }
                ],
                'max_tokens': 300
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', 
                                   headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return self._generate_synthetic_insights(trend_data)
                
        except Exception as e:
            print(f"AI API Error: {e}")
            return self._generate_synthetic_insights(trend_data)
    
    def _prepare_data_summary(self, trend_data):
        """Prepare data summary for AI analysis"""
        popular_routes = trend_data.get('popular_routes', [])[:5]
        demand_analysis = trend_data.get('demand_analysis', {})
        
        summary = f"""
        Top 5 Popular Routes: {[r['route'] for r in popular_routes]}
        Average Prices: {[r['avg_price'] for r in popular_routes]}
        Popular Destinations: {[d['destination'] for d in demand_analysis.get('popular_destinations', [])[:3]]}
        High Demand Periods: {len(demand_analysis.get('high_demand_periods', []))} periods identified
        """
        
        return summary
    
    def _generate_synthetic_insights(self, trend_data):
        """Generate synthetic insights when AI API is unavailable"""
        insights = [
            "Sydney-Melbourne corridor shows highest demand with premium pricing opportunities for nearby hostels.",
            "Weekend travel peaks suggest hostels should optimize pricing for Friday-Sunday arrivals.",
            "International gateway cities (Sydney, Melbourne, Brisbane) show consistent high-volume traffic.",
            "Price sensitivity appears lower on popular tourist routes, indicating premium accommodation demand.",
            "Seasonal variations suggest dynamic pricing strategies would benefit hostel revenue optimization."
        ]
        
        return " ".join(random.sample(insights, 3))

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/collect-data')
def collect_data():
    """API endpoint to collect and process flight data"""
    try:
        # Collect flight data
        collector = AirlineDataCollector()
        flights = collector.get_flight_data(limit=200)
        
        # Store in database
        analyzer = TrendAnalyzer()
        analyzer.store_flight_data(flights)
        
        return jsonify({
            'success': True,
            'message': f'Successfully collected {len(flights)} flight records',
            'flights_collected': len(flights)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-trends')
def analyze_trends():
    """API endpoint to analyze market trends"""
    try:
        analyzer = TrendAnalyzer()
        
        # Get popular routes
        popular_routes = analyzer.get_popular_routes(limit=15)
        
        # Get demand analysis
        demand_analysis = analyzer.get_demand_analysis()
        
        # Get price trends
        price_trends_df = analyzer.get_price_trends()
        
        # Generate AI insights
        ai_generator = AIInsightGenerator()
        trend_data = {
            'popular_routes': popular_routes,
            'demand_analysis': demand_analysis
        }
        ai_insights = ai_generator.generate_market_insights(trend_data)
        
        return jsonify({
            'success': True,
            'popular_routes': popular_routes,
            'demand_analysis': demand_analysis,
            'price_trends': price_trends_df.to_dict('records') if not price_trends_df.empty else [],
            'ai_insights': ai_insights
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/visualizations')
def get_visualizations():
    """API endpoint to generate visualization data"""
    try:
        analyzer = TrendAnalyzer()
        
        # Popular routes chart
        popular_routes = analyzer.get_popular_routes(limit=10)
        
        routes_chart = {
            'data': [{
                'x': [r['route'] for r in popular_routes],
                'y': [r['flight_count'] for r in popular_routes],
                'type': 'bar',
                'marker': {'color': '#3B82F6'},
                'name': 'Flight Count'
            }],
            'layout': {
                'title': 'Most Popular Flight Routes',
                'xaxis': {'title': 'Routes'},
                'yaxis': {'title': 'Number of Flights'},
                'height': 400
            }
        }
        
        # Price trends chart
        price_trends_df = analyzer.get_price_trends()
        
        if not price_trends_df.empty:
            # Get top 5 routes for cleaner visualization
            top_routes = price_trends_df.groupby('route')['flight_count'].sum().nlargest(5).index
            filtered_df = price_trends_df[price_trends_df['route'].isin(top_routes)]
            
            price_chart = {
                'data': [],
                'layout': {
                    'title': 'Price Trends Over Time (Top 5 Routes)',
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Average Price ($)'},
                    'height': 400
                }
            }
            
            for route in top_routes:
                route_data = filtered_df[filtered_df['route'] == route].sort_values('date')
                price_chart['data'].append({
                    'x': route_data['date'].tolist(),
                    'y': route_data['avg_price'].tolist(),
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'name': route
                })
        else:
            price_chart = {
                'data': [],
                'layout': {
                    'title': 'Price Trends Over Time',
                    'annotations': [{
                        'text': 'No price trend data available',
                        'showarrow': False,
                        'xref': 'paper',
                        'yref': 'paper',
                        'x': 0.5,
                        'y': 0.5
                    }]
                }
            }
        
        # Demand analysis chart
        demand_analysis = analyzer.get_demand_analysis()
        destinations = demand_analysis.get('popular_destinations', [])
        
        demand_chart = {
            'data': [{
                'labels': [d['destination'] for d in destinations],
                'values': [d['arrival_count'] for d in destinations],
                'type': 'pie',
                'hole': 0.3,
                'marker': {'colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']}
            }],
            'layout': {
                'title': 'Popular Destinations Distribution',
                'height': 400
            }
        }
        
        return jsonify({
            'success': True,
            'charts': {
                'popular_routes': routes_chart,
                'price_trends': price_chart,
                'demand_distribution': demand_chart
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# HTML Templates
def create_templates():
    """Create HTML templates"""
    os.makedirs('templates', exist_ok=True)
    
    # Main template
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airline Market Demand Analyzer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-blue-600 text-white shadow-lg">
            <div class="container mx-auto px-4 py-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h1 class="text-3xl font-bold">Airline Market Demand Analyzer</h1>
                        <p class="text-blue-100 mt-2">Market Intelligence for Australian Hostel Groups</p>
                    </div>
                    <div class="flex space-x-4">
                        <button id="collectDataBtn" class="bg-blue-500 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors">
                            <i class="fas fa-download mr-2"></i>Collect Data
                        </button>
                        <button id="analyzeBtn" class="bg-green-500 hover:bg-green-700 px-4 py-2 rounded-lg transition-colors">
                            <i class="fas fa-chart-line mr-2"></i>Analyze Trends
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container mx-auto px-4 py-8">
            <!-- Status Bar -->
            <div id="statusBar" class="mb-6 p-4 bg-white rounded-lg shadow-md hidden">
                <div class="flex items-center">
                    <div id="statusIcon" class="mr-3"></div>
                    <div id="statusMessage" class="text-gray-700"></div>
                </div>
            </div>

            <!-- Loading Indicator -->
            <div id="loadingIndicator" class="hidden mb-6">
                <div class="flex justify-center items-center p-8">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    <span class="ml-4 text-gray-600">Processing data...</span>
                </div>
            </div>

            <!-- Dashboard Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <!-- Quick Stats -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
                    <div id="quickStats" class="space-y-3">
                        <div class="text-gray-600">Click "Collect Data" to start</div>
                    </div>
                </div>

                <!-- Top Routes -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Top Routes</h3>
                    <div id="topRoutes" class="space-y-2">
                        <div class="text-gray-600">No data available</div>
                    </div>
                </div>

                <!-- AI Insights -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">
                        <i class="fas fa-robot mr-2 text-blue-600"></i>AI Insights
                    </h3>
                    <div id="aiInsights" class="text-gray-600 text-sm">
                        Run analysis to get AI-powered market insights
                    </div>
                </div>
            </div>

            <!-- Visualizations -->
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
                <!-- Popular Routes Chart -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Popular Routes</h3>
                    <div id="popularRoutesChart" class="h-96"></div>
                </div>

                <!-- Price Trends Chart -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Price Trends</h3>
                    <div id="priceTrendsChart" class="h-96"></div>
                </div>
            </div>

            <!-- Demand Distribution -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Demand Distribution</h3>
                <div id="demandChart" class="h-96"></div>
            </div>

            <!-- Detailed Data Table -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Detailed Route Analysis</h3>
                <div class="overflow-x-auto">
                    <table id="routeTable" class="w-full table-auto">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 py-2 text-left">Route</th>
                                <th class="px-4 py-2 text-left">Cities</th>
                                <th class="px-4 py-2 text-left">Flights</th>
                                <th class="px-4 py-2 text-left">Avg Price</th>
                                <th class="px-4 py-2 text-left">Demand Score</th>
                            </tr>
                        </thead>
                        <tbody id="routeTableBody">
                            <tr>
                                <td colspan="5" class="px-4 py-8 text-center text-gray-500">
                                    No data available. Click "Analyze Trends" to populate the table.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-800 text-white text-center py-6 mt-12">
            <p>&copy; 2024 Airline Market Demand Analyzer. Built for Australian Hostel Groups.</p>
        </footer>
    </div>

    <script>
        // Application state
        let appState = {
            dataCollected: false,
            analysisComplete: false
        };

        // Utility functions
        function showLoading() {
            document.getElementById('loadingIndicator').classList.remove('hidden');
        }

        function hideLoading() {
            document.getElementById('loadingIndicator').classList.add('hidden');
        }

        function showStatus(message, type = 'info') {
            const statusBar = document.getElementById('statusBar');
            const statusIcon = document.getElementById('statusIcon');
            const statusMessage = document.getElementById('statusMessage');
            
            statusBar.classList.remove('hidden');
            statusMessage.textContent = message;
            
            // Set icon and color based on type
            if (type === 'success') {
                statusIcon.innerHTML = '<i class="fas fa-check-circle text-green-500"></i>';
                statusBar.className = 'mb-6 p-4 bg-green-50 border border-green-200 rounded-lg shadow-md';
            } else if (type === 'error') {
                statusIcon.innerHTML = '<i class="fas fa-exclamation-circle text-red-500"></i>';
                statusBar.className = 'mb-6 p-4 bg-red-50 border border-red-200 rounded-lg shadow-md';
            } else {
                statusIcon.innerHTML = '<i class="fas fa-info-circle text-blue-500"></i>';
                statusBar.className = 'mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg shadow-md';
            }
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                statusBar.classList.add('hidden');
            }, 5000);
        }

        // Data collection
        async function collectData() {
            showLoading();
            showStatus('Collecting flight data from APIs...', 'info');
            
            try {
                const response = await fetch('/api/collect-data');
                const data = await response.json();
                
                if (data.success) {
                    appState.dataCollected = true;
                    showStatus(`Successfully collected ${data.flights_collected} flight records`, 'success');
                    updateQuickStats(data.flights_collected);
                } else {
                    showStatus(`Error: ${data.error}`, 'error');
                }
            } catch (error) {
                showStatus(`Network error: ${error.message}`, 'error');
            } finally {
                hideLoading();
            }
        }

        // Trend analysis
        async function analyzeData() {
            if (!appState.dataCollected) {
                showStatus('Please collect data first before analyzing trends', 'error');
                return;
            }
            
            showLoading();
            showStatus('Analyzing market trends and generating insights...', 'info');
            
            try {
                // Get trend analysis
                const trendResponse = await fetch('/api/analyze-trends');
                const trendData = await trendResponse.json();
                
                if (trendData.success) {
                    appState.analysisComplete = true;
                    updateDashboard(trendData);
                    
                    // Get visualizations
                    const vizResponse = await fetch('/api/visualizations');
                    const vizData = await vizResponse.json();
                    
                    if (vizData.success) {
                        updateCharts(vizData.charts);
                        showStatus('Analysis complete! Market insights generated.', 'success');
                    } else {
                        showStatus('Analysis complete, but visualization generation failed', 'error');
                    }
                } else {
                    showStatus(`Analysis failed: ${trendData.error}`, 'error');
                }
            } catch (error) {
                showStatus(`Analysis error: ${error.message}`, 'error');
            } finally {
                hideLoading();
            }
        }

        // Update dashboard components
        function updateQuickStats(flightCount) {
            const quickStats = document.getElementById('quickStats');
            quickStats.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="text-gray-600">Flights Collected:</span>
                    <span class="font-semibold text-blue-600">${flightCount}</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-gray-600">Data Status:</span>
                    <span class="font-semibold text-green-600">Ready</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-gray-600">Last Updated:</span>
                    <span class="font-semibold text-gray-600">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        }

        function updateDashboard(data) {
            // Update top routes
            const topRoutes = document.getElementById('topRoutes');
            const routes = data.popular_routes.slice(0, 5);
            
            topRoutes.innerHTML = routes.map(route => `
                <div class="flex justify-between items-center py-1 border-b border-gray-100">
                    <div>
                        <div class="text-sm font-medium text-gray-800">${route.route}</div>
                        <div class="text-xs text-gray-500">${route.cities}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-semibold text-blue-600">${route.flight_count}</div>
                        <div class="text-xs text-gray-500">${route.avg_price}</div>
                    </div>
                </div>
            `).join('');

            // Update AI insights
            const aiInsights = document.getElementById('aiInsights');
            aiInsights.innerHTML = `
                <div class="text-sm text-gray-700 leading-relaxed">
                    ${data.ai_insights}
                </div>
            `;

            // Update detailed table
            updateRouteTable(data.popular_routes);
        }

        function updateRouteTable(routes) {
            const tbody = document.getElementById('routeTableBody');
            
            tbody.innerHTML = routes.map(route => `
                <tr class="border-b border-gray-100 hover:bg-gray-50">
                    <td class="px-4 py-3 font-medium text-gray-800">${route.route}</td>
                    <td class="px-4 py-3 text-gray-600">${route.cities}</td>
                    <td class="px-4 py-3 text-center">
                        <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
                            ${route.flight_count}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-green-600 font-semibold">${route.avg_price}</td>
                    <td class="px-4 py-3">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-600 h-2 rounded-full" style="width: ${route.avg_demand * 10}%"></div>
                        </div>
                        <span class="text-xs text-gray-500 mt-1">${route.avg_demand}/10</span>
                    </td>
                </tr>
            `).join('');
        }

        function updateCharts(charts) {
            // Popular routes chart
            if (charts.popular_routes && charts.popular_routes.data.length > 0) {
                Plotly.newPlot('popularRoutesChart', charts.popular_routes.data, charts.popular_routes.layout, {
                    responsive: true,
                    displayModeBar: false
                });
            }

            // Price trends chart
            if (charts.price_trends && charts.price_trends.data.length > 0) {
                Plotly.newPlot('priceTrendsChart', charts.price_trends.data, charts.price_trends.layout, {
                    responsive: true,
                    displayModeBar: false
                });
            } else {
                document.getElementById('priceTrendsChart').innerHTML = `
                    <div class="flex items-center justify-center h-full text-gray-500">
                        <div class="text-center">
                            <i class="fas fa-chart-line text-4xl mb-4"></i>
                            <p>No price trend data available</p>
                        </div>
                    </div>
                `;
            }

            // Demand distribution chart
            if (charts.demand_distribution && charts.demand_distribution.data.length > 0) {
                Plotly.newPlot('demandChart', charts.demand_distribution.data, charts.demand_distribution.layout, {
                    responsive: true,
                    displayModeBar: false
                });
            }
        }

        // Event listeners
        document.getElementById('collectDataBtn').addEventListener('click', collectData);
        document.getElementById('analyzeBtn').addEventListener('click', analyzeData);

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            showStatus('Welcome! Click "Collect Data" to start analyzing airline market trends.', 'info');
        });
    </script>
</body>
</html>'''

    with open('templates/index.html', 'w') as f:
        f.write(index_html)

# Main application setup
def setup_app():
    """Setup the complete application"""
    # Initialize database
    init_db()
    
    # Create templates
    create_templates()
    
    print("✅ Application setup complete!")
    print("📊 Airline Market Demand Analyzer Ready")
    print("🔧 Database initialized")
    print("🎨 Templates created")

if __name__ == '__main__':
    setup_app()
    
    print("\n" + "="*50)
    print("🚀 Starting Airline Market Demand Analyzer")
    print("="*50)
    print("📍 Server: http://localhost:5000")
    print("🔑 Environment Variables (Optional):")
    print("   - AVIATIONSTACK_API_KEY: For real flight data")
    print("   - OPENAI_API_KEY: For AI insights")
    print("💡 Without API keys, synthetic data will be used")
    print("="*50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)