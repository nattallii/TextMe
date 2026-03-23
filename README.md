# TextMe
TaskBoardApp is a microservices-based backend application built with FastAPI.
The system is designed as a set of independent services responsible for authentication, user profiles, chats and real-time messages.

## Tech Stack

### Backend

**FastAPI**  
High-performance Python web framework used to build REST APIs.  
Provides automatic OpenAPI/Swagger documentation, request validation, and async support.

**Pydantic**  
Used for data validation and settings management.

**uv**  
Fast Python package and environment manager written in Rust.  
Used as a modern replacement for pip, pip-tools, and virtualenv.

**SQLAlchemy / Alembic**  
SQLAlchemy is used as the ORM for database interaction.  
Alembic is used for database schema migrations.

---

### Databases

**PostgreSQL**  
Relational database used independently by the Auth Service and Profile Service.  
This follows the database-per-service approach and keeps service data isolated.

**MongoDB**  
NoSQL database used by the Chat Service for storing chat-related data.

---

### Containerization

**Docker**  
Used to containerize each microservice and its dependencies.

**Docker Compose**  
Used for local development to run services and databases in a simple way.

---

### Orchestration

**Kubernetes (Minikube)**  
Local Kubernetes cluster used to simulate a production-like environment.

**Helm**  
Package manager for Kubernetes used to:
- deploy services consistently
- manage configuration through values files
- simplify upgrades and re-deployments

---

### CI/CD

**GitHub Actions**  
Used to automate CI pipelines for:
- building Docker images
- pushing images to Docker Hub

---

## Architecture Overview

The project is built as a microservices-based web application.

### Services

**Auth Service**  
Responsible for user registration, login, and authentication.

**Profile Service**  
Responsible for managing user profile data.

**Chat Service**  
Responsible for chat-related functionality and message handling.

### Databases

**Auth Service → PostgreSQL**  
Stores authentication-related data such as users.

**Profile Service → PostgreSQL**  
Stores user profile information.

**Chat Service → MongoDB**  
Stores chat-related data.

### Infrastructure

**Kubernetes + Helm**  
Used for deploying all services and databases in the `textme` namespace.

**Migration Jobs**  
Alembic migrations are executed as Kubernetes Jobs during deployment for services that use PostgreSQL.

---

## Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

---

## Contributing

Contributors should follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for commit messages.

---

## How to Start the Project

### Run Locally with Docker

#### Requirements

- Docker Desktop
- Docker Compose v2

#### Verify installation

```bash
docker version
docker compose version
```
### Start the Application:
1. From the project **root** (where docker-compose.yml is):


`docker compose up -d --build  `

This command will:

- build all Docker images

- start all services and databases

- expose APIs on localhost


2. Open FastAPI docs:

- http://localhost:8000/docs - auth service

- http://localhost:8002/docs - profile service

- http://localhost:8001/docs - chat service

Register user:

**POST** /api/v1/auth/register


Example body:

```
{
  "username": "Natali",
  "password": "1!Stringst",
  "phone": "+380688186966"
}
```

Login:

**POST** /api/v1/auth/login


Example body:
````
{
  "phone": "+380688186966",
  "password": "1!Stringst"
}

````

### Connect to PostgreSQL (Auth Service)
Check if the user was created:
```
docker exec -it fastapiproject-auth_db-1 psql -U authuser -d authdb
\dt
SELECT * FROM users;
```

### Stop Containers
```
docker compose down
```