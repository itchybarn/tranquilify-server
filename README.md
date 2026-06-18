# Tranquilify Server

The backend API for Tranquilify, a misophonia headphones project. Built with FastAPI, PostgreSQL, and Docker.

## Prerequisites

Ensure everything on this list is as-stated before beginning the setup.

- **Docker** running

## First-time setup

1. Clone the repo.
2. Copy the env template:
   ```bash
   cp .env.example .env
   ```

## Running

1. After cloning, run:
   ```bash
   alembic upgrade head
   docker compose up db -d
   . .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. Then you can run API commands against http://localhost
