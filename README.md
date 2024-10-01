# Movie Night Together

**Movie Night Together** is a web application API designed to help friends and family organize movie nights seamlessly. Users can search for movies, create movie night events, invite others, and receive notifications—all within a user-friendly interface.

## Table of Contents

- [Features]
- [Tech Stack]
- [Installation and Usage]
- [Accessibility]
- [Docker Compose Configuration]
- [API Documentation]
- [Testing]
- [Contact]

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
- **Authentication**: Djoser, JWT, google-auth(Google)
- **Asynchronous Tasks**: Celery, Redis
- **Database**:  SQLite for Dev (PostgreSQL for Prod)
- **External APIs**: OMDb API
- **Testing**: Pytest, Factory Boy
- **Documentation**: Swagger/OpenAPI
- **Docker**: Dockerfile/Docker Compose

## Installation and Usage

### Prerequisites

- **Docker and Docker Compose installed on your system.**


### Clone the Repository

```bash
https://github.com/nldq092203/Movie-Night.git
cd Movie-Night

```

### Environment Variables

```bash
# Django settings
SECRET_KEY=your_secret_key
DEBUG=True

# Database settings
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db
DB_HOST = db
DB_PORT = 5432

# Redis settings
REDIS_URL=redis://redis:6379/0

# External API keys
OMDB_API_KEY=your_omdb_api_key
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_client_id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_client_secret
```

### Docker Setup

#### 1. Build and Start Containers:

```bash
docker-compose up --build

```

#### 2.Run Database Migrations (Optional)

```bash
docker-compose exec web python manage.py migrate

```

#### 3. Create a Superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

#### 4. Stop the application
```bash
docker-compose down
```

## Accessibility
### Accessing the Application

- Visit `http://localhost:8000/` to access the application.
- Admin interface at `http://localhost:8000/admin/`.

### API Endpoints

- **Authentication**: `/auth/`
- **Movies**: `/api/v1/movies/`
- **Movie Nights**: `/api/v1/movienights/`
- **Invitations**: `/api/v1/invitations/`

## Docker Compose Configuration
The docker-compose.yml file includes services for:

- **web: The Django application.**
- **db: PostgreSQL database.**
- **redis: Redis server for Celery.**
- **celery: Celery worker for asynchronous tasks.**
- **celery-beat: Celery Beat scheduler for periodic tasks.**
    

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


```bash
docker-compose exec web pytest
```
### Mocking External Services

Use mocking to simulate external API calls (e.g., OMDb API) during tests to avoid hitting real endpoints.

## Contact

- **Author**: NGUYEN Le Diem Quynh
- **Email**: lnguye220903@gmail.com
- **GitHub**: nldq092203
