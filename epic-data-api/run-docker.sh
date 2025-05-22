#!/bin/bash

# Build and start the Docker containers
echo "Building and starting containers..."
docker-compose up -d

# Wait for the application to start
echo "Waiting for the application to start..."
sleep 5

# Display logs
echo "Application is running! Showing logs:"
docker-compose logs -f 