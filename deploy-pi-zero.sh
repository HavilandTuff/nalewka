#!/bin/bash
# Deployment script for Raspberry Pi Zero

# This script sets up the Nalewka application on a Raspberry Pi Zero

echo "Starting Nalewka deployment for Raspberry Pi Zero..."

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: This script is designed for Raspberry Pi Zero. You might be on a different system."
fi

# Update system packages
echo "Updating system packages..."
sudo apt update

# Install Python and pip if not already installed
echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Create project directory
echo "Creating project directory..."
mkdir -p ~/nalewka
cd ~/nalewka

# Clone the repository (replace with your actual repository URL)
# git clone https://github.com/yourusername/nalewka.git .
# For now, we'll assume the files are already copied to this directory

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-pi-zero.txt

# Set up environment variables
echo "Setting up environment variables..."
mkdir -p instance
cat > .env << EOF
FLASK_APP=nalewka.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this-in-production
# Using SQLite for Pi Zero deployment (in instance folder for security)
DATABASE_URL=sqlite:///instance/nalewka.db
EOF

# Initialize the database
echo "Initializing database..."
flask init-db

# Optional: Seed with sample data
echo "Seeding database with sample data..."
flask seed-data

echo "Deployment complete!"
echo ""
echo "To start the application, run:"
echo "  cd ~/nalewka"
echo "  source venv/bin/activate"
echo "  flask run --host=0.0.0.0 --port=5000"
echo ""
echo "The application will be accessible at http://[PI_ZERO_IP]:5000"
echo "Replace [PI_ZERO_IP] with your Raspberry Pi Zero's IP address"
