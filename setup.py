#!/usr/bin/env python3
"""
Setup script for Airline Market Demand Analyzer
Automates the installation and setup process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🛩️  AIRLINE MARKET DEMAND ANALYZER SETUP  🛩️        ║
    ║                                                              ║
    ║              Setting up your market intelligence tool        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]} (Compatible)")

def setup_virtual_environment():
    """Create and setup virtual environment"""
    print("\n🔧 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("   Do you want to recreate it? (y/N): ")
        if response.lower() == 'y':
            print("🗑️  Removing existing virtual environment...")
            shutil.rmtree(venv_path)
        else:
            print("✅ Using existing virtual environment")
            return
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # macOS/Linux
        pip_path = Path("venv/bin/pip")
    
    if not pip_path.exists():
        print("❌ Virtual environment not found. Please run setup again.")
        sys.exit(1)
    
    try:
        print("   Installing packages from requirements.txt...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Please check your internet connection and try again")
        sys.exit(1)

def setup_environment_file():
    """Setup environment variables file"""
    print("\n🔑 Setting up environment variables...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return
    
    if env_example.exists():
        print("📋 Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("✅ .env file created")
        print("   💡 Edit .env file to add your API keys (optional)")
    else:
        print("⚠️  .env.example not found, creating basic .env file...")
        with open(env_file, 'w') as f:
            f.write("""# Airline Market Demand Analyzer Environment Variables
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Optional API Keys
AVIATIONSTACK_API_KEY=
OPENAI_API_KEY=

# Database
DATABASE_URL=airline_data.db
""")
        print("✅ Basic .env file created")

def create_run_script():
    """Create platform-specific run scripts"""
    print("\n🚀 Creating run scripts...")
    
    # Windows batch script
    if os.name == 'nt':
        with open("run.bat", "w") as f:
            f.write("""@echo off
echo Starting Airline Market Demand Analyzer...
call venv\\Scripts\\activate
python app.py
pause
""")
        print("✅ Windows run script created: run.bat")
    
    # Unix shell script
    with open("run.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Starting Airline Market Demand Analyzer..."
source venv/bin/activate
python app.py
""")
    
    # Make shell script executable
    try:
        os.chmod("run.sh", 0o755)
        print("✅ Unix run script created: run.sh")
    except:
        print("⚠️  Unix run script created but may need chmod +x run.sh")

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    # Determine python path
    if os.name == 'nt':
        python_path = Path("venv/Scripts/python")
    else:
        python_path = Path("venv/bin/python")
    
    try:
        # Test imports
        test_script = """
import flask
import requests
import pandas
import plotly
import numpy
print("✅ All dependencies imported successfully")
"""
        
        result = subprocess.run([str(python_path), "-c", test_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation test passed")
        else:
            print("❌ Installation test failed")
            print(f"   Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Installation test failed: {e}")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. 🔑 Edit .env file to add your API keys (optional)")
    print("2. 🚀 Run the application:")
    
    if os.name == 'nt':
        print("   Windows: Double-click run.bat OR run: python app.py")
    else:
        print("   Unix/Mac: ./run.sh OR python app.py")
    
    print("3. 🌐 Open browser to: http://localhost:5000")
    print("4. 📊 Click 'Collect Data' then 'Analyze Trends'")
    
    print("\n💡 Tips:")
    print("• App works without API keys using synthetic data")
    print("• Get free AviationStack API key for real flight data")
    print("• Add OpenAI API key for AI-powered insights")
    print("• Check README.md for detailed documentation")
    
    print("\n🆘 Support:")
    print("• Documentation: README.md")
    print("• Issues: Check troubleshooting section")
    print("• API Keys: See .env.example for instructions")
    
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print_banner()
    
    try:
        check_python_version()
        setup_virtual_environment()
        install_dependencies()
        setup_environment_file()
        create_run_script()
        test_installation()
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()