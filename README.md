# Airline Market Demand Analyzer 🛩️

A comprehensive Python web application for analyzing airline booking trends and market demand patterns, specifically designed for hostel groups in Australia.

## 🚀 Features

- **Real-time Data Collection**: Integrates with AviationStack API for live flight data
- **Market Trend Analysis**: Identifies popular routes, pricing patterns, and demand fluctuations
- **AI-Powered Insights**: Uses OpenAI API to generate market intelligence summaries
- **Interactive Dashboard**: Modern web interface with real-time charts and visualizations
- **Australian Focus**: Specifically analyzes major Australian airports and routes
- **Hostel Business Intelligence**: Tailored insights for accommodation providers

## 📋 Requirements

```txt
Flask==2.3.3
requests==2.31.0
pandas==2.1.4
plotly==5.17.0
numpy==1.24.3
python-dotenv==1.0.0
sqlite3
```

## 🔧 Installation & Setup

### 1. Clone or Download the Project

```bash
# Create project directory
mkdir airline-demand-analyzer
cd airline-demand-analyzer

# Copy the main application file (save as app.py)
# Copy requirements.txt
# Copy .env.example
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Setup (Optional)

Create a `.env` file in the project root:

```env
# Optional: For real flight data (free tier available)
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here

# Optional: For AI insights (requires OpenAI account)
OPENAI_API_KEY=your_openai_api_key_here

# Flask configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔑 API Keys (Optional)

### AviationStack API (Free Tier)
- Sign up at [aviationstack.com](https://aviationstack.com)
- Free tier: 1,000 requests/month
- Provides real-time flight data

### OpenAI API (Paid)
- Sign up at [platform.openai.com](https://platform.openai.com)
- Used for AI-generated market insights
- Minimal usage cost (~$0.01 per analysis)

**Note**: Without API keys, the application will use synthetic data for demonstration purposes.

## 📊 How to Use

1. **Start the Application**
   ```bash
   python app.py
   ```

2. **Collect Flight Data**
   - Click "Collect Data" button
   - App fetches ~200 flight records
   - Data is stored in local SQLite database

3. **Analyze Market Trends**
   - Click "Analyze Trends" button
   - Generates insights about popular routes
   - Creates price trend analysis
   - Displays demand patterns

4. **View Results**
   - Interactive charts and visualizations
   - Detailed route analysis table
   - AI-generated market insights
   - Export-ready data views

## 🏗️ Project Structure

```
airline-demand-analyzer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
├── airline_data.db       # SQLite database (auto-created)
├── templates/
│   └── index.html        # Main dashboard template (auto-created)
├── static/               # Static files (if needed)
└── README.md            # This file
```

## 🎯 Business Applications

### For Hostel Operators:
- **Location Intelligence**: Identify high-traffic airports and routes
- **Pricing Strategy**: Understand demand patterns for dynamic pricing
- **Marketing Timing**: Target campaigns during peak travel periods
- **Capacity Planning**: Anticipate guest volume based on flight patterns

### Key Metrics Tracked:
- Most popular flight routes
- Average airfare pricing trends
- Seasonal demand variations
- Airport traffic patterns
- Travel destination preferences

## 🔍 Technical Features

### Data Collection:
- **Primary**: AviationStack API integration
- **Fallback**: Synthetic data generation for demo
- **Storage**: SQLite database for persistence
- **Processing**: Pandas for data manipulation

### Analysis Engine:
- Route popularity ranking
- Price trend calculation
- Demand score analysis
- Temporal pattern recognition

### Visualization:
- Interactive Plotly charts
- Real-time data updates
- Responsive design
- Mobile-friendly interface

### AI Integration:
- OpenAI GPT integration
- Context-aware insights
- Business-focused recommendations
- Fallback synthetic insights

## 🚨 Troubleshooting

### Common Issues:

1. **Module Not Found Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **API Rate Limits**
   - AviationStack: 1,000 requests/month on free tier
   - OpenAI: Pay-per-use pricing
   - App automatically falls back to synthetic data

3. **Database Issues**
   - Delete `airline_data.db` to reset
   - App will recreate database on next run

4. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill process using port 5000

### Performance Tips:
- Use real APIs for production deployment
- Consider caching for frequently accessed data
- Implement data retention policies for database growth
- Use environment variables for configuration

## 📈 Future Enhancements

- [ ] Real-time data streaming
- [ ] Advanced predictive analytics
- [ ] Email report automation
- [ ] Multi-region support
- [ ] API rate limiting and caching
- [ ] User authentication
- [ ] Data export functionality
- [ ] Mobile app companion
