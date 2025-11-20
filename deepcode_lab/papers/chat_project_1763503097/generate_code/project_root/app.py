from flask import Flask
from config import Config

# Initialize the Flask application
app = Flask(__name__)

# Load configurations
app.config.from_object(Config)

# Placeholder for blueprint registration
# from your_blueprint import your_blueprint
# app.register_blueprint(your_blueprint)

# Define a simple route for testing
@app.route('/')
def home():
    return "Welcome to the Secure Login Module!"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)