# Movie Night Together

**Movie Night Together** is a web application API designed to help friends and family organize movie nights seamlessly. Users can search for movies, create movie night events, invite others, and receive notifications—all within a user-friendly interface.

## Table of Contents

- [Features]
- [Tech Stack]
- [Installation]
- [Configuration]
- [Usage]
- [API Documentation]
- [Testing]
- [Contact](https://www.notion.so/README-10d68b6fcc4780dabebddfc1b00336ec?pvs=21)

## Features

- **User Authentication and Authorization**: Secure user registration and login using JWT tokens. And integrate with Google Auth
- **Movie Search**: Search for movies using the OMDb API and save them locally.
- **Movie Details**: View detailed information about movies, including genres and full descriptions.
- **Movie Night Creation**: Organize movie nights and invite friends.
- **Invitations**: Send and manage invitations for movie nights.
- **Notifications**: Receive email notifications for invitations and reminders.
- **Filtering and Ordering**: Filter and sort movies and movie nights based on various criteria.
- **Asynchronous Tasks**: Utilize Celery for long-running tasks and scheduled notifications.
- **Throttling and Pagination**: Control API usage and paginate results for efficient data handling.
- **CORS Support**: Cross-Origin Resource Sharing is enabled for API accessibility.
- **API Documentation**: Comprehensive API docs generated with Swagger/OpenAPI.

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Authentication**: Djoser, JWT, Allauth (Google)
- **Asynchronous Tasks**: Celery, Redis
- **Database**:  SQLite for Dev (PostgreSQL for Prod)
- **External APIs**: OMDb API
- **Testing**: Pytest, Factory Boy
- **Documentation**: Swagger/OpenAPI

## Installation

### Prerequisites

- Python 3.9 or higher
- Redis (for Celery broker)
- PostgreSQL (or another database)
- Node.js and npm (for frontend development, if applicable)

### Clone the Repository

```bash
https://github.com/nldq092203/Movie-Night.git
cd Movie-Night

```

### Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate

```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root and configure the following variables:

```

SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/movienightdb
REDIS_URL=redis://localhost:6379/0
OMDB_API_KEY=your_omdb_api_key

```

### Apply Migrations

```bash
python manage.py migrate

```

### Create a Superuser

```bash
python manage.py createsuperuser

```

### Install Redis (if not already installed)

For macOS:

```bash
brew install redis
brew services start redis

```

For Ubuntu:

```bash
sudo apt-get install redis-server
sudo systemctl enable redis-server.service

```

## Configuration

### Django Settings

The project uses `django-configurations` and `dj-database-url` for settings management.

- **settings.py**: Contains the base configuration using class-based settings.
- **wsgi.py** and **manage.py**: Updated to use `django-configurations`.

### Celery Configuration

- **Broker**: Redis
- **Backend**: Redis
- **Start Celery Worker**:
    
    ```bash
    celery -A movienight worker -l DEBUG                          
    ```
    
- **Start Celery Beat Scheduler**:
    
    ```bash
    celery -A movienight beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
    
    ```
    

## Usage

### Running the Development Server

```bash
python manage.py runserver

```

### Accessing the Application

- Visit `http://localhost:8000/` to access the application.
- Admin interface at `http://localhost:8000/admin/`.

### API Endpoints

- **Authentication**: `/auth/`
- **Movies**: `/api/v1/movies/`
- **Movie Nights**: `/api/v1/movienights/`
- **Invitations**: `/api/v1/invitations/`

## API Documentation

The API is documented using Swagger/OpenAPI.

### Generating API Schema

```bash
python manage.py spectacular --file schema.yaml

```

### Generating TypeScript Types (Optional)

```bash
npx openapi-typescript schema.yaml --output types.ts

```

### Accessing Swagger UI

Visit [`http://localhost:8000/schema/swagger-ui](http://127.0.0.1:8000/api/schema/swagger-ui)/` to view the interactive API documentation.

## Testing

### Running Tests

```bash
pytest
```

### Testing Tools

- **Pytest**: Testing framework.
- **Factory Boy**: For creating test data.
- **APIClient**: To simulate API requests in tests.

### Testing Components

- **Models**: Test the integrity and behavior of models.
- **Views and APIs**: Test API endpoints, permissions, filters, and pagination.
- **Tasks**: Test Celery tasks and scheduled jobs.
- **Serializers**: Ensure data serialization and deserialization works as expected.

### Mocking External Services

Use mocking to simulate external API calls (e.g., OMDb API) during tests to avoid hitting real endpoints.

## Contact

- **Author**: NGUYEN Le Diem Quynh
- **Email**: lnguye220903@gmail.com
- **GitHub**: nldq092203
