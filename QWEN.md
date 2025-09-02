# Nalewka - Liquor Management System

## Project Overview

Nalewka is a Flask-based web application for managing homemade liquor recipes and batches. The application allows users to track their liquor production, including ingredients, batch formulas, and production metrics.

### Main Technologies
- **Backend**: Python 3.9+ with Flask framework
- **Database**: SQLAlchemy ORM with Alembic migrations, supporting SQLite (development) and PostgreSQL (production)
- **Frontend**: Jinja2 templates with HTML/CSS
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and validation
- **Configuration**: Pydantic Settings for environment-based configuration
- **Deployment**: Render hosting with Gunicorn WSGI server

### Core Features
- User authentication (registration, login, logout)
- Liquor management (create and track different types of liquors)
- Batch tracking with detailed ingredient formulas
- Ingredient database with descriptions
- Recipe management with precise measurements
- Bottle tracking (count and volume)
- Volume unit conversion utilities

## Project Structure

```
nalewka/
├── app/                    # Main application package
│   ├── __init__.py        # Flask app initialization
│   ├── models.py          # Database models (User, Liquor, Ingredient, Batch, BatchFormula)
│   ├── forms.py           # WTForms definitions
│   ├── routes.py          # Application routes/blueprints
│   ├── services.py        # Business logic layer
│   ├── repositories.py    # Data access layer
│   ├── utils.py           # Utility functions
│   └── templates/         # HTML templates
├── migrations/            # Database migrations (Alembic)
├── tests/                 # Test suite
├── config.py              # Configuration settings (Pydantic)
├── nalewka.py             # Application entry point and CLI commands
├── deploy.py              # Deployment script
├── build.sh               # Build script for Render
├── render.yaml            # Render configuration
├── requirements.txt       # Production dependencies
└── README.md              # Project documentation
```

## Database Schema

The application uses a relational database with the following models:

1. **User**: User accounts with authentication
2. **Liquor**: Represents different types of liquors, linked to users
3. **Ingredient**: Database of available ingredients
4. **Batch**: Specific batches of liquor, linked to liquors
5. **BatchFormula**: Links batches to ingredients with quantities and units

## Development Workflow

### Environment Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements-dev.txt` (for development) or `pip install -r requirements.txt` (for production)

### Configuration
Environment variables are managed through:
- `.env` file (loaded automatically)
- System environment variables
- Pydantic Settings in `config.py`

Key variables:
- `SECRET_KEY`: Required for session security
- `DATABASE_URL`: Database connection URI
- Mail server settings for notifications
- OAuth settings for Google authentication
- reCAPTCHA keys for form protection

### Running the Application Locally
1. Set environment variables:
   ```bash
   export FLASK_APP=nalewka.py
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key-here
   ```
2. Initialize the database: `flask init-db`
3. (Optional) Create sample data: `flask seed-data`
4. Run the development server: `flask run`

### Database Management
- Initialize database: `flask init-db`
- Reset database: `flask reset-db`
- Create migrations: `flask db migrate -m "Description of changes"`
- Apply migrations: `flask db upgrade`

### Testing
Run tests with pytest:
```bash
pytest
```

### Code Quality
- Formatting: `black .`
- Linting: `ruff check .`
- Type checking: `mypy .` (partially implemented)

## Deployment

The application is designed for deployment on Render:

1. The `render.yaml` file defines the web service and database
2. The `build.sh` script installs dependencies and sets up the database
3. The start command uses Gunicorn: `gunicorn --bind 0.0.0.0:$PORT nalewka:app`
4. Environment variables are configured in the Render dashboard

For manual deployment:
1. Install production dependencies: `pip install -r requirements.txt`
2. Set required environment variables
3. Run database migrations: `flask db upgrade`
4. Start the server: `gunicorn --bind 0.0.0.0:$PORT nalewka:app`

## Key Design Patterns

### Repository Pattern
Data access is abstracted through repository classes in `app/repositories.py`, separating data access logic from business logic.

### Service Layer
Business logic is encapsulated in service functions in `app/services.py`, keeping routes clean and focused on HTTP concerns.

### Form Validation
WTForms are used for input validation with custom validators for business rules.

## Development Conventions

- Follow PEP 8 style guide with Black formatting
- Use type hints where possible
- Write unit tests for new functionality
- Use the repository pattern for database interactions
- Keep business logic in service functions
- Handle errors gracefully with appropriate flash messages
- Use meaningful commit messages and follow semantic versioning

## Refactoring Status

According to TODO.md, the project has completed Phase 1 and Phase 2 refactoring tasks:
- Code formatting and linting with Black and Ruff
- Enhanced dependency management with pip-tools
- Comprehensive test suite with pytest
- Strengthened service layer and repository pattern
- Improved configuration management with Pydantic

Ongoing work includes:
- Enforcing static typing with mypy
- Refactoring to a REST API
- Centralizing error handling

## Default Credentials (for sample data)
- Username: admin
- Password: password123
