# Nalewka - Liquor Management System

A Flask-based web application for managing homemade liquor recipes and batches.

## Features

- **User Authentication**: Secure login and registration system
- **Liquor Management**: Create and manage different types of liquors
- **Batch Tracking**: Record batches with detailed ingredient formulas
- **Ingredient Database**: Maintain a database of ingredients with descriptions
- **Recipe Management**: Store and track liquor recipes with precise measurements

## Local Development

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd nalewka
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   - For production, install from `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```
   - For development, install from `requirements-dev.txt`:
     ```bash
     pip install -r requirements-dev.txt
     ```

### Dependency Management

This project uses `pip-tools` to manage dependencies.

- Application dependencies are defined in `requirements.in`.
- Development dependencies are defined in `requirements-dev.in`.

To update the compiled `requirements.txt` and `requirements-dev.txt` files after changing the `.in` files, run the following commands:

```bash
pip-compile requirements.in
pip-compile requirements-dev.in
```


4. **Set up environment variables**:
   ```bash
   export FLASK_APP=nalewka.py
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key-here
   ```

5. **Initialize the database**:
   ```bash
   python manage.py init
   ```

6. **Create sample data (optional)**:
   ```bash
   python manage.py sample
   ```

### Running Locally

```bash
flask run
```

The application will be available at `http://localhost:5000`

### Default Login (if using sample data)

- **Username**: admin
- **Password**: password123

## Deployment on Render

### Prerequisites

- A Render account
- Your code pushed to a Git repository (GitHub, GitLab, etc.)

### Deployment Steps

1. **Connect your repository to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "Web Service"
   - Connect your Git repository

2. **Configure the service**:
   - **Name**: `nalewka-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT nalewka:app`

3. **Add environment variables**:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a secure random string
   - `DATABASE_URL`: Will be automatically set when you add a database

4. **Add a PostgreSQL database**:
   - In your Render dashboard, click "New +" and select "PostgreSQL"
   - Name it `nalewka-db`
   - Copy the connection string to your environment variables

5. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### Using render.yaml (Alternative)

If you prefer to use the `render.yaml` file:

1. Push your code with the `render.yaml` file to your repository
2. In Render dashboard, click "New +" and select "Blueprint"
3. Connect your repository
4. Render will automatically create the web service and database

### Post-Deployment Setup

After deployment, you need to initialize the database:

1. **Access your application** and note the URL
2. **Run database initialization** (you can do this via Render's shell or by adding a build script):
   ```bash
   python deploy.py --sample
   ```

### Environment Variables for Production

Make sure these are set in your Render service:

- `FLASK_ENV`: `production`
- `SECRET_KEY`: A secure random string
- `DATABASE_URL`: PostgreSQL connection string (auto-set by Render)

## Database Schema

### Users
- Store user account information
- Each user can have multiple liquors

### Liquors
- Represents different types of liquors
- Contains name, description, and creation date
- Linked to user who created it

### Ingredients
- Database of available ingredients
- Contains name and description
- Used across multiple batches

### Batches
- Represents a specific batch of liquor
- Contains description and creation date
- Linked to a specific liquor

### Batch Formulas
- Links batches to ingredients
- Contains quantity and unit measurements
- Allows precise recipe tracking

## Project Structure

```
nalewka/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── api.py               # API endpoints
│   ├── api_utils.py         # API utility functions
│   ├── auth_utils.py        # Authentication utilities
│   ├── error_handlers.py    # Centralized error handlers
│   ├── exceptions.py        # Custom exception classes
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms definitions
│   ├── routes.py            # Application routes
│   ├── services.py          # Business logic services
│   ├── repositories.py      # Data access repositories
│   └── templates/           # HTML templates
├── migrations/              # Database migrations
├── docs/                   # API documentation
│   ├── api_documentation.yaml  # OpenAPI/Swagger specification
│   └── API_DOCUMENTATION.md    # Documentation guide
├── config.py               # Configuration settings
├── nalewka.py              # Application entry point
├── manage.py               # Management script
├── deploy.py               # Deployment script
├── build.sh                # Build script for Render
├── render.yaml             # Render configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Development

### Adding New Features

1. **Models**: Add new database models in `app/models.py`
2. **Forms**: Create forms in `app/forms.py`
3. **Routes**: Add routes in `app/routes.py`
4. **Templates**: Create HTML templates in `app/templates/`

### Database Migrations

When you modify models, create a new migration:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## API

The Nalewka application provides a comprehensive REST API for programmatic access to all features. The API is versioned and follows REST principles with consistent error handling and response formats.

### API Documentation

Interactive API documentation is available at `/api/v1/docs` when the application is running. The documentation includes:

- Detailed descriptions of all endpoints
- Request/response schemas
- Example requests and responses
- Authentication requirements

The raw OpenAPI/Swagger specification is available in the `docs/api_documentation.yaml` file. For more details, see `docs/API.md`.

### Authentication

Most API endpoints require authentication using a JWT token. To obtain a token:

1. POST to `/api/v1/auth/login` with username and password
2. Use the returned token in the Authorization header:
   ```
   Authorization: Bearer <your-token>
   ```

### API Endpoints

The API includes endpoints for:

- User management (`/api/v1/users`)
- Liquor management (`/api/v1/liquors`)
- Ingredient management (`/api/v1/ingredients`)
- Batch management (`/api/v1/batches`)
- Formula management (`/api/v1/formulas`)
- API key management (`/api/v1/auth/api-keys`)

- **Password Hashing**: Passwords are securely hashed using Werkzeug
- **CSRF Protection**: All forms include CSRF tokens
- **Authentication Required**: Protected routes require login
- **Input Validation**: All user inputs are validated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
