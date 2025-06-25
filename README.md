# Time Table Scheduler

A web-based application for university timetable scheduling using a Genetic Algorithm. Built with Django, PostgreSQL, Celery, Redis, and Docker.

## Live Demo
[Smart Timetable Scheduler](https://smart-tts.onrender.com/)

_Live scheduling unavailable due to hosting costs_

## Screenshots

![Dashboard](https://github.com/user-attachments/assets/97f4d7cc-48ac-4577-86c6-21111451dcac)
![Timetable](https://github.com/user-attachments/assets/768b7c1b-e734-48e8-be0c-08a7ca8acfd6)


## Prerequisites

- [Docker](https://www.docker.com/) / Docker Desktop installed on your system.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Om-Raj/Time-Table-Scheduler.git
cd Time-Table-Scheduler
```

### 2. Create a `.env` File

Create a `.env` file in the root directory with the following content:

```dotenv
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

# PostgreSQL connection
DATABASE_URL=your_postgres_url

# Redis
REDIS_URL=redis://redis:6379/0
```

> Replace `your-secret-key` and `your_postgres_url` with appropriate values.

### 3. Start the Application

Use Docker Compose to build and start the containers:

```bash
docker compose down  # Optional: clean up existing containers
docker compose up -d --build
```

The application will be accessible at `http://localhost:8000` (or the configured port).

## Stopping the Application

To stop and remove the containers:

```bash
docker compose down
```
