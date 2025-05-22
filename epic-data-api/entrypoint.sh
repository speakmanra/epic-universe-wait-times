#!/bin/bash

# Check if we're using PostgreSQL
if [ "$USE_POSTGRES" = "True" ]; then
    echo "Using PostgreSQL database..."
    
    # PostgreSQL variables from DATABASE_URL
    DB_HOST="db"
    DB_PORT="5432"
    DB_USER="epic_user"
    DB_PASSWORD="epic_password"
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d epic_data -c '\q'; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    
    echo "PostgreSQL is up - continuing"
else
    echo "Using SQLite database..."
    # Wait a moment for the file system to be ready
    sleep 2
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create logs directory if it doesn't exist
mkdir -p /var/log/epic-data

# Start server with Gunicorn
echo "Starting Gunicorn server..."
/usr/local/bin/gunicorn epic_data.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/epic-data/gunicorn-access.log \
    --error-logfile /var/log/epic-data/gunicorn-error.log \
    --user root \
    --group root 