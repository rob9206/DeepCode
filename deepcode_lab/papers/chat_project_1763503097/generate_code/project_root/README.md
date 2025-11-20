# Secure Login Module with Flask and JWT

## Description
This project is a secure login system using the Flask web framework and JWT for token-based authentication. It provides a basic web application interface with login and dashboard pages, ensuring secure password storage and user data management.

## Project Structure
- **app.py**: Entry point and Flask app initialization
- **authentication.py**: Handles login, logout, and JWT token management
- **models.py**: Defines user model and database interactions
- **config.py**: Configuration for Flask and JWT
- **requirements.txt**: Dependencies for the project
- **utils.py**: Utility functions for security and validation
- **templates/**: Contains HTML templates for login and dashboard pages
- **static/**: Contains CSS for styling the application

## Setup Instructions
1. Clone the repository.
2. Navigate to the project directory.
3. Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask application:
   ```bash
   flask run
   ```

## Dependencies
- Flask==2.1.0
- PyJWT==2.6.0
- Flask-SQLAlchemy==2.5.1
- Werkzeug==2.1.0

Optional:
- Flask-Cors: To handle cross-origin resource sharing if needed.
- Flask-Migrate: Database migrations if using SQLAlchemy.

## Features
- User authentication using JWT tokens.
- Secure password storage and user data management.
- Basic web application interface with login and dashboard pages.

## Security
This application implements security best practices such as password hashing and JWT token management to ensure secure user authentication and data protection.

## Testing
Test the login module for security vulnerabilities and correct JWT functionality.