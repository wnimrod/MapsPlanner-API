# MapsPlanner_API

This project was generated using fastapi_template.

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m MapsPlanner_API
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here. 
 
The file structure is as the following:

```
host=
port=
db_host=
db_port=
db_user=
db_pass=
db_base=

backend_url=
frontend_url=

google_auth_client_id=
google_auth_client_secret=

chatgpt_api_key=

user_auto_approval=

environment=

log_level=

# Docker compose

POSTGRES_PASSWORD=
POSTGRES_USER=
POSTGRES_DB=
```


An example of `.env` file:

```
host=0.0.0.0
port=8888
db_host=maps_planner_api-db
db_port=5432
db_user=maps_planner_api
db_pass=maps_planner_api
db_base=maps_planner_api

backend_url=http://localhost:8888
frontend_url=http://localhost:5173

google_auth_client_id=<google_auth_client_id>
google_auth_client_secret=<google_auth_client_secret>

chatgpt_api_key=<chatgpt_api_key>

user_auto_approval=True

environment=local

log_level=DEBUG


# Docker compose

POSTGRES_PASSWORD=maps_planner_api
POSTGRES_USER=maps_planner_api
POSTGRES_DB=maps_planner_api
```

## Makefile

common commands can be found under the `Makefile` file.

In order to use the `make` command, you need to install the `make` tool.

You can read more about make here: https://www.gnu.org/software/make/

* Building a fresh development image and start running containers:

```bash
make build-dev
```

* Restarting existing development containers:
```bash
make start-dev
```
Development image supports hot refresh.

* Stop all containers:
```bash
make stop
```

## Project structure

```bash
MapsPlanner_API
├── db  # module contains db configurations
│   └── models  # Package contains different models for ORMs.
├── tests  # Test assets for project
├── web  # Package contains web server. Handlers, startup config.
│    ├── api  # Package with all handlers.
│    │   └── router.py  # Main router.
│    ├── application.py  # FastAPI application configuration.
│    └── lifetime.py  # Contains actions to perform on startup and shutdown.
├── conftest.py  # Fixtures for all tests.
├── __main__.py  # Startup script. Starts uvicorn.
├── settings.py  # Main configuration settings for project.
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* autoflake (removes unused imports and unused variables);
* black (formats your code);


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

You can override test environment variables using `.env.pytest` file.

If you want to run it in docker, simply run:

```bash
make test
```

For running tests on your local machine.
1. you need to start a database.

```bash
make start
```


2. Run the pytest.
```bash
poetry run pytest -vv . -W ignore --html=pytest-report.html --self-contained-html
```
