# Epic Universe Data Tracker

A Django application that fetches, stores, and displays historical data from Universal's Epic Universe theme park.

## Features

- Fetches live data from the theme park API every minute
- Stores historical information about attractions and shows
- Tracks wait times, operating status, and showtimes
- Provides a web interface to view current park status
- Includes a JSON API endpoint for current wait times
- Admin interface for viewing historical data
- Dual database setup: PostgreSQL for Docker, SQLite for local development

## Installation

### Option 1: Using Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository
3. Navigate to the project directory
4. Run the application with Docker Compose:
   ```
   docker-compose up -d
   ```
5. Create a superuser (optional):
   ```
   docker-compose exec web python manage.py createsuperuser
   ```
6. Access the application at `http://localhost:8000/`

When using Docker, the application automatically uses PostgreSQL as the database. The data is persisted in a Docker volume named `postgres_data`.

### Option 2: Manual Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate.fish  # For fish shell users
   # OR
   source venv/bin/activate  # For bash/zsh users
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables (copy `.env.example` to `.env` and edit as needed)
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```

When running locally, the application uses SQLite by default. If you want to use PostgreSQL locally, you can set the `DATABASE_URL` and `USE_POSTGRES=True` environment variables.

## Configuration

Configuration is handled through environment variables, which can be set in a `.env` file or in the Docker Compose file:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to "True" for development, "False" for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `THEME_PARK_API_BASE_URL`: Base URL for the theme park API
- `THEME_PARK_ENTITY_ID`: Entity ID for the theme park to track
- `DATABASE_URL`: PostgreSQL connection string (used only when `USE_POSTGRES` is "True")
- `USE_POSTGRES`: Set to "True" to use PostgreSQL, otherwise uses SQLite

## Database Setup

The application supports two database backends:

1. **SQLite** (default for local development):
   - Simple, file-based database
   - No additional setup required
   - Data stored in `db.sqlite3` file

2. **PostgreSQL** (used in Docker):
   - More powerful and scalable
   - Set `USE_POSTGRES=True` and provide a `DATABASE_URL`
   - Format: `postgresql://username:password@host:port/database_name`

## Data Collection

The application automatically collects data from the theme park API every minute using a scheduled task. This data is stored in the database for historical tracking and analysis.

## Usage

- Web Interface: Visit `http://localhost:8000/` to see the current park status
- API: Access `http://localhost:8000/park/api/current-waits/` for JSON data of current wait times
- Admin Interface: Visit `http://localhost:8000/admin/` to view and manage all data (requires login)
- Historical Data: Click on any attraction name to view historical wait time charts

## Docker Commands

- Start the application:
  ```
  docker-compose up -d
  ```

- View logs:
  ```
  docker-compose logs -f
  ```

- Stop the application:
  ```
  docker-compose down
  ```

- Stop the application and remove volumes (this will delete all data):
  ```
  docker-compose down -v
  ```

- Run a command in the container:
  ```
  docker-compose exec web [command]
  ```
  
- Example: Run migrations:
  ```
  docker-compose exec web python manage.py migrate
  ```

- Connect to the PostgreSQL database:
  ```
  docker-compose exec db psql -U epic_user -d epic_data
  ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 