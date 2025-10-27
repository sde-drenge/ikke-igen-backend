# ikke-igen-backend

A Django REST Framework project for building REST APIs.

## Features

- Django 4.2
- Django REST Framework 3.16
- CORS headers support
- Environment-based configuration with python-decouple
- SQLite database (default)

## Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sde-drenge/ikke-igen-backend.git
cd ikke-igen-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

- `GET /api/` - API root (lists available endpoints)
- `GET /api/health/` - Health check endpoint
- `GET /admin/` - Django admin interface

## Configuration

Configuration is managed through environment variables using python-decouple. You can set these in a `.env` file or as system environment variables:

- `SECRET_KEY` - Django secret key (required for production)
- `DEBUG` - Debug mode (default: True)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts (default: *)
- `CORS_ALLOW_ALL_ORIGINS` - Allow all CORS origins (default: True)
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

## Development

### Project Structure

```
ikke-igen-backend/
├── api/                 # Main API app
│   ├── views.py        # API views
│   ├── urls.py         # API URL routing
│   └── ...
├── config/             # Django project configuration
│   ├── settings.py     # Project settings
│   ├── urls.py         # Root URL configuration
│   └── ...
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Running Tests

```bash
python manage.py test
```

## License

This project is licensed under the MIT License.
