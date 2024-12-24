# Movie Night Together 

***Movie Night Together*** is a full-stack web application designed as a social platform to simplify organizing movie night events. With Movie Night Together, users can effortlessly search for movies, create and manage events, invite friends, receive notifications, and chat individually or in groups—all within an intuitive and user-friendly interface.

## Demo Video
https://github.com/nldq092203/Movie-Night.git/Demo.mp4

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [CI/CD](#ci/cd)
- [Accessibility](#accessibility)
- [Database UML Diagram](#database-uml-diagram)
- [Development](#development)
  - [Installation and Usage](#installation-and-usage)
    - [Prerequisites](#prerequisites)
    - [Clone the Repository](#clone-the-repository)
    - [Environment Variables](#environment-variables)
    - [Docker Setup](#docker-setup)

  - [API Documentation](#api-documentation)
  - [Testing](#testing)
    - [Running Tests](#running-tests)
    - [Testing Tools](#testing-tools)
    - [Testing Components](#testing-components)
    - [Mocking External Services](#mocking-external-services)
- [Contact](#contact)

## Accessibility

- Visit [Project Website](https://movienight-ui-550865855378.europe-west9.run.app) to access the live application.
- Visit [Movie-Night-UI](https://github.com/nldq092203/Movie-Night-UI.git) to access Frontend project.

## Features
🔐 User Authentication and Authorization

	•	JWT Authentication: Secure login and registration with JSON Web Tokens (JWT) for session management.
	•	Google OAuth2 Integration: Simplified login with Google accounts for faster access.

🕒 Asynchronous Tasks

	•	Background Processing with Celery and Redis: Offload heavy operations and enable scheduled notifications using Celery and Redis.

🔄 Real-Time Chat with WebSockets

	•	Instant Messaging: Real-time chatbox to communicate instantly with other users, powered by WebSocket technology.

🎥 Movie Management

	•	Movie Search: Search movies using the OMDb API, and store data locally for quicker future access.
	•	Detailed Movie Pages: View extensive details, including genres, ratings, and descriptions.

🎬 Movie Night Event Organization

	•	Create and Manage Events: Organize and manage movie nights, including scheduling, invite management, and start time updates.
	•	Invitation System: Send, manage, and confirm invitations for movie nights with real-time updates.
  
🎬 Event Notifications

	•	Reminders: Stay updated with timely reminders before your upcoming movie nights.
	•	Event Updates: Instantly notified of start time adjustments or event cancellations.
	•	New Invitations: Receive alerts when you’re invited to new movie nights.
	•	Invitation Confirmations: As a host, get notified when invitees confirm their attendance.

💬 Chatbox Features

	•	Private and Group Chat Creation: Easily set up chat groups for private or public discussions.
	•	Nickname Customization: Assign nicknames in group chats for personalized interactions.
	•	Message Search: Search messages and chatbox names to quickly locate conversations.

👤 User Profile Management

	•	Profile Customization: Update your avatar, name, gender, bio, and manage your personal event schedule.

🔎 Advanced Filtering and Sorting

	•	Enhanced Data Navigation: Filter and sort data across movies, events, notifications, chat groups, and messages for a tailored user experience.

📊 API Throttling and Pagination

	•	Efficient Data Handling: Control API usage and retrieve data in paginated results to optimize load times and performance.

🌍 CORS Support

	•	Cross-Origin Resource Sharing: Safely enable cross-origin access for broader accessibility to your application.

📄 Comprehensive API Documentation

	•	Swagger/OpenAPI Documentation: Easily reference API endpoints, request parameters, and responses with well-organized documentation.

⚙️ TypeScript Support

	•	Static Typing: Utilize custom types and interfaces for robust, consistent data structures and improved code quality.

## Tech Stack
### Backend
- **Frameworks**: Django, Django REST Framework (DRF)
- **Authentication**: Djoser, JWT, Google OAuth2
- **Web Socket**: Ably (third party)
- **Asynchronous and Scheduled Tasks**: Celery, Redis
- **Database**: PostgreSQL (SQLite for test)
- **Cloud Storage**: Firebase
- **External APIs**: OMDb API
- **Documentation**: Swagger/OpenAPI
- **Containerization**: Docker, Docker Compose
- **TypeScript**: For shared data structures and contracts

### Frontend

- **Framework**: React.js 
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **HTTP Client**: Axios
- **Build Tool**: Vite

### CI/CD
- **Source Control**: GitHub
- **CI/CD Pipeline**: Github Action
- **Build Tools**: Docker
- **Testing**: Pytest, Factory Boy, APIClient, Postman
- **Deployment**: Google Cloud Run, Railway
## Database UML Diagram
Below is the database UML diagram illustrating the data structure:
![Database UML Diagram](./movienight-uml.drawio.png)

## Development
### Installation and Usage

#### Prerequisites

- Docker & Docker Compose: Ensure both are installed on your system.

#### Clone the Repository
##### Backend Repo
```bash
https://github.com/nldq092203/Movie-Night.git
cd Movie-Night

```

##### Frontend Repo
```bash
git clone https://github.com/nldq092203/Movie-Night-UI.git
cd Movie-Night-UI
```

#### Environment Variables
```bash
# Django settings
SECRET_KEY=your_secret_key

# Database settings
DATABASE_URL=your_database_url

# Redis settings
REDIS_URL=your_redis_url

# External API keys
OMDB_KEY=your_omdb_api_key
SOCIAL_CLIENT_SECRET=your_google_client_secret
GOOGLE_CLIENT_ID=your_google_client_id
ABLY_API_KEY=your_ably_api_key
FIREBASE_ADMINSDK_KEY=your_firebase_key
```

#### Docker Setup

##### 1. Build and Start Containers:

```bash
docker-compose up --build

```

##### 2.Run Database Migrations (Optional)

```bash
docker-compose exec web python manage.py migrate

```

##### 3. Create a Superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

##### 4. Stop the application
```bash
docker-compose down
```


### API Documentation

The API is documented using Swagger/OpenAPI.
Swagger UI: 
Accessible at `http://localhost:8000/api/schema/swagger-ui`.

#### Generating API Schema

```bash
python manage.py spectacular --file schema.yaml

```

#### Generating TypeScript Types (Optional)

```bash
npx openapi-typescript schema.yaml --output types.ts

```

### Testing

#### Running Tests

```bash
docker-compose exec web pytest
```

#### Testing Tools

- **Pytest**: Testing framework.
- **Factory Boy**: For creating test data.
- **APIClient**: To simulate API requests in tests.

#### Testing Components

- **Models**: Test the integrity and behavior of models.
- **Views and APIs**: Test API endpoints, permissions, filters, and pagination.
- **Tasks**: Test Celery tasks and scheduled jobs.
- **Serializers**: Ensure data serialization and deserialization works as expected.
- **URLs**: Test that all routes are correctly mapped and accessible, and that they return the expected responses. 

#### Mocking External Services

Use mocking to simulate external API calls (e.g., OMDb API) during tests to avoid hitting real endpoints.

## Contact

- **Author**: NGUYEN Le Diem Quynh
- **Email**: lnguye220903@gmail.com
- **GitHub**: nldq092203
