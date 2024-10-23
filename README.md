# Workout Tracker API

Welcome! This project is a **Django-based application** designed for users to track their workouts and progress.

Below, you'll find the **requirements**, **installation instructions**, **testing information**, and **custom commands** to help you work with the project.

## Requirements

Before starting, ensure you have the following tools installed:

- **Python 3.10+**
- **pip (Python package manager)**
- **Virtualenv (optional, recommended for virtual environments)**
- **PostgreSQL**

### Dependencies

The main dependencies are listed in the `requirements.txt` file, including:

- Django Rest Framework
- pytest + plugins for testing
- psycopg3 (for PostgreSQL support)
- Other packages as needed for specific functionality

## Instalation

Follow these steps to set up the application locally:

### 1. Clone the repository

```bash
git clone https://github.com/gocardless/sample-django-app.git
cd sample-django-app
```

### 2. Create a virtual environment (optional)

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a .env file in the root of the project with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=host1,host2   # comma separated list
CORS_ALLOWED_ORIGINS=https://host1.com,https://host2.net    # comma separated list

DATABASE_NAME=database-name
DATABASE_USER=database-user
DATABASE_PASSWORD=database-password
DATABASE_PORT=database-port
DATABASE_HOST=database-host

CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
```

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Load initial data for exercises and categories (optional)

```bash
python manage.py populate_exercises
```

### 7. Run the development server

```bash
python manage.py runserver
```

The app will be available at http://localhost:8000.

## Testing

We use pytest for automated testing. Ensure that the testing dependencies are installed.

### Run tests:

```bash
# All tests
pytest
```

```bash
# Unit tests
pytest -m unit
```

```bash
# Integration tests
pytest -m integration
```

### Generate a coverage report:

```bash
pytest --cov=my_app   # you can add any other pytest command
```

We are using pytest-django so the tests will be run on a temporary database, leaving the main one intact.


## Extra commands

Here are some useful commands available in the application:

### Create a superuser

```bash
python manage.py createsuperuser
```

### Dump the database to a file

```bash
python manage.py dumpdata --format=json --indent=2 > backup.json
```

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
