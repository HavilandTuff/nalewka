#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python deploy.py

echo "Build completed successfully!"
