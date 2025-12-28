#!/bin/bash
# Backup script for Nalewka SQLite database
# This script creates a timestamped backup and removes versions older than 7 days.

# Configuration
APP_DIR="/home/karol/nalewka"
DB_PATH="$APP_DIR/instance/nalewka.db"
BACKUP_DIR="$APP_DIR/backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/nalewka_backup_$TIMESTAMP.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup at $(date)"

# Use sqlite3 to perform a safe online backup
if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"
else
    echo "Error: sqlite3 not found. Please install it with 'sudo apt install sqlite3'"
    exit 1
fi

# Check if backup was successful
if [ $? -eq 0 ]; then
    # Compress the backup
    gzip "$BACKUP_FILE"
    echo "Backup successful: ${BACKUP_FILE}.gz"

    # Set restrictive permissions
    chmod 600 "${BACKUP_FILE}.gz"

    # Remove backups older than retention period
    find "$BACKUP_DIR" -name "nalewka_backup_*.db.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old backups cleaned up."
else
    echo "Error: Database backup failed."
    exit 1
fi

echo "Backup process completed at $(date)"
