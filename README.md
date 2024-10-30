# Workout Tracker API

Welcome! This project is a **Django-based application** designed for users to track their workouts and progress.

Below, you'll find the **requirements**, **installation instructions**, **accessing the Admin Dashboard**, **API documentation**, **testing information**, **Celery and Celery Beat execution**, and **extra commands**.


## Requirements

Before starting, ensure you have the following tools installed:

- **Python 3.10+**
- **pip** (Python package manager)
- **Virtualenv** (optional, recommended for virtual environments)
- **PostgreSQL**
- **Redis or RabbitMQ** (as the message broker for Celery)

### Dependencies

The main dependencies are listed in the `requirements.txt` file, including:

- Django Rest Framework
- pytest + plugins for testing
- psycopg3 (for PostgreSQL support)
- Celery
- drf-spectacular (for API documentation)
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


## Accessing the Admin Dashboard

If you have superuser permissions, you can access the **Admin Dashboard** at the following URL:

- **Admin Dashboard**: http://localhost:8000/admin/

To log in, use the superuser credentials you created using the command:

```bash
python manage.py custom_createsuperuser   # This command is customized to consider social authentication
```

This dashboard allows you to manage application data and users effectively.


## API Documentation with Swagger

This application provides API documentation using Swagger. You can access the interactive API documentation UI at the following URLs:

- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/

These endpoints will give you an overview of the available API endpoints and allow you to test them interactively.


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


## Running Celery

To run Celery, open a new terminal window and navigate to your project directory, then execute the following command:

```bash
celery -A workout_tracker worker --loglevel=INFO
```
Workout_tracker is the name of the Django application

### Running Celery Beat

To run Celery Beat, which is used for scheduling tasks, open another terminal window and execute:

```bash
celery -A workout_tracker beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

This will start the scheduler that sends tasks to the Celery worker based on the schedule you define in your Django application.


## Extra commands

Here are some useful commands available in the application:

### Create a superuser

```bash
python manage.py createsuperuser
```

### Populate the database with exercises and categories

```bash
python manage.py populate_exercises
```

This command populates the database with sample data for exercises and their respective categories.

### Dump the database to a file

```bash
python manage.py dumpdata --format=json --indent=2 > backup.json
```

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
