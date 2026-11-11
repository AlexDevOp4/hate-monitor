# Monitor

Full-stack app: Django + Django REST Framework + PostgreSQL backend, React + TypeScript + Vite frontend, run with Docker Compose.

## Setup

```sh
cp .env.example .env   # then set DJANGO_SECRET_KEY
```

## Start the stack

```sh
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/api/health/

Both services hot-reload on code changes. Add `-d` to run in the background.

## Stop the stack

```sh
docker compose down
```

Add `-v` to also delete the PostgreSQL data volume.

## Run Django migrations

```sh
docker compose exec backend python manage.py migrate
```

To create migrations after model changes:

```sh
docker compose exec backend python manage.py makemigrations
```

## Run Django tests

```sh
docker compose exec backend python manage.py test
```

## Build the frontend

```sh
docker compose exec frontend npm run build
```
# hate-monitor
