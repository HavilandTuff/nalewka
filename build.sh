#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Initialize database and run migrations
echo "Setting up database..."
flask db upgrade

echo "Build completed successfully!" 