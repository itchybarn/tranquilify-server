# Tranquilify Server

The backend API for Tranquilify, a misophonia headphones project. Built with FastAPI, PostgreSQL, and Docker.

---

# Using the Server

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

1. Start the database first (migrations and the app both need it up):
   ```bash
   docker compose up db -d
   ```
2. Activate your virtual environment and apply the database migrations:
   ```bash
   . .venv/bin/activate
   alembic upgrade head
   ```
3. Start the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Then you can run API commands against http://localhost

The database must be running before `alembic upgrade head`, and migrations must be applied before starting the app. The app does not create tables on startup.

## Routes

### /docs

FastAPI's built in endpoint testing suite. contains all currently available endpoints as well as the ability to designate auth headers.

### /user

Creates a user. Requires a specific JSON request body:
```json
{
   "login_credentials": {
      "username": "string",
      "password": "string with length 8 minimum"
   },
   "auth_method": "+1 444-444-4444"
}
```

### /login

**(WIP)**: when implemented, logging in can be done with a password or a code sent to the phone number registered to the account. the requester must provide a string for either option (```"password"``` or ```"code"```) as the value for the ```login_method```

Will require this JSON request body:

```json
{
   username: "string"
   login_method: "password or code"
   login_value: "value needed for login method"
}
```

### /auth/send

Sends a 4-6 digit code to the user's phone number they provided in account creation. It also allows the server to send a code to the correct phone number

---

# About the Repository

## Database & Migrations

The database schema is managed with [Alembic](https://alembic.sqlalchemy.org/). `alembic upgrade head` builds and updates the schema.

`init_db()` in `app/db/session.py` creates all tables directly from the models, without Alembic. It is intended for tests and throwaway local databases, and is not called on app startup.

### Commands

- Apply all pending migrations (upgrade the schema to the latest revision):
  ```bash
  alembic upgrade head
  ```
- Show the current database revision:
  ```bash
  alembic current
  ```
- Show migration history:
  ```bash
  alembic history --verbose
  ```
- Roll back the most recent migration:
  ```bash
  alembic downgrade -1
  ```

### Creating a migration after changing a model

After adding or changing a model in `app/models/`, generate a migration from the diff, then apply it:

```bash
alembic revision --autogenerate -m "[short description of the change]"
alembic upgrade head
```

New model files must be imported in `alembic/env.py` for autogenerate to detect their tables, e.g. `import app.models.new_model  # noqa: F401` (comment suppresses linter error).
