# ProHub API

A simple REST API for product management built with **FastAPI**, **PostgreSQL**, and **Redis**.

## Tech Stack

- Python 3.11
- FastAPI, Pydantic
- SQLAlchemy
- PostgreSQL
- Redis
- Alembic
- Pytest
- Docker & Docker Compose

For each stack versions, kindly check requirements.txt

## Features

- JWT Authentication & Authorization
- Product CRUD
- Pagination, Sorting, and Filtering
- Redis Caching
- Automated Testing

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/gilbertopatricklie/ProHub.git
cd ProHub
```

**2. Create and activate virtual environment**

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file and configure the required environment variables, including:

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Also configure the PostgreSQL environment file required by Docker Compose.

**5. Start PostgreSQL and Redis**

```bash
docker compose up -d
```

**6. Run database migrations**

```bash
alembic upgrade head
```

**7. Start the application**

```bash
python -m uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, open:

- Swagger UI: http://127.0.0.1:8000/docs

## Running Tests

```bash
python -m pytest tests -v
```

## License

This project was developed for learning and portfolio purpose only.