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

## Routes:

### /docs

FastAPI's built in endpoint testing suite. contains all currently available endpoints as well as the ability to designate auth headers.

### /user

Creates a user. Requires a specific JSON request body:
```json
{
   username: "string",
   password: "string with length 8 minimum",
   auth_method: "+1 444-444-4444"
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


