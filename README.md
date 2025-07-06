# Australian Flight Demand Analyzer

A Python web application that scrapes real-time flight data from multiple sources and provides AI-powered market demand insights specifically tailored for hostel businesses across Australia.

## 🚀 Live Demo

Access the application at: `http://localhost:5000` (after setup)

## 📋 Overview

This web application helps hostel owners understand airline booking market demand by:
- Scraping real-time flight data from FlightAware and FlightRadar24
- Analyzing flight patterns, airline market share, and demand trends
- Providing AI-generated insights for business planning
- Visualizing data through interactive charts and tables

## 🛠️ Technical Approach

### Data Collection Strategy
1. **Primary Source**: FlightAware flight arrival data
2. **Secondary Source**: FlightRadar24 API for additional coverage
3. **Fallback**: Realistic synthetic data when scraping fails
4. **Compliance**: Respects rate limits and terms of service

### Data Processing Pipeline
1. **Scraping**: BeautifulSoup + requests for web scraping
2. **Cleaning**: pandas for data normalization and processing
3. **Analysis**: Statistical analysis of flight patterns
4. **Insights**: OpenAI GPT-3.5 for intelligent market insights
5. **Visualization**: Chart.js for interactive data visualization

### Architecture
- **Backend**: Flask web framework
- **Frontend**: Bootstrap 5 + Chart.js for responsive UI
- **Data Processing**: pandas for efficient data manipulation
- **AI Integration**: OpenAI API for market insights
- **Scraping**: requests + BeautifulSoup for data extraction

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for data scraping

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Airline-Market-Demand-Analy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys (Optional)**
   - Edit `config.py`
   - Replace `'your-api-key-here'` with your OpenAI API key for AI insights
   - If no API key provided, the app will use rule-based insights

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Select an Australian airport (SYD, MEL, BNE, PER, ADL, DRW)
   - Click "Analyze Market Demand"

### Detailed Setup

#### Step 1: Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configuration
Edit `config.py` to customize:
- Request delays between scraping attempts
- API keys for enhanced insights
- User agent strings for scraping

#### Step 3: Optional OpenAI Integration
For AI-powered insights:
1. Get an OpenAI API key from https://platform.openai.com/
2. Replace `'your-api-key-here'` in `config.py`
3. The app works without this key using rule-based insights

#### Step 4: Running the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🖥️ Usage Guide

### Basic Usage
1. **Select Airport**: Choose from 6 major Australian airports
2. **Analyze**: Click the analyze button to scrape real-time data
3. **View Results**: Get comprehensive insights including:
   - Flight volume and airline market share
   - Peak demand hours and popular routes
   - On-time performance metrics
   - AI-generated business insights

### Features
- **Real-time Data**: Live flight information from multiple sources
- **Smart Analytics**: AI-powered market demand insights
- **Interactive Charts**: Visual representation of flight patterns
- **Responsive Design**: Works on desktop and mobile devices
- **Business Focus**: Insights tailored for hostel operations

## 📊 Data Sources

1. **FlightAware**: Primary source for arrival data
2. **FlightRadar24**: Secondary API for additional coverage
3. **OpenSky Network**: Aviation statistics
4. **Synthetic Data**: Realistic fallback when scraping fails

## 🔍 Key Insights Provided

### Market Demand Analysis
- Peak travel hours for optimal hostel check-in timing
- Popular routes indicating high-demand corridors
- Airline market share for partnership opportunities
- Seasonal patterns for capacity planning

### Performance Metrics
- On-time performance affecting guest arrival predictability
- Flight volume trends for demand forecasting
- Origin distribution for targeted marketing

### Business Intelligence
- Optimal pricing strategies based on demand patterns
- Staff scheduling recommendations
- Marketing timing for maximum impact
