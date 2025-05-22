FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=epic_data.settings

# Set work directory
WORKDIR /app

# Install PostgreSQL client libraries and other dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh
RUN chmod +x healthcheck.sh

# Configure healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD ["./healthcheck.sh"]

# Run entrypoint script
CMD ["./entrypoint.sh"] 