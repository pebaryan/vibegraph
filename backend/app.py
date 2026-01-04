from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import route modules to register endpoints
from backend.routes import graphs, queries, search

# Register routes (the decorators in each module will automatically register to app)

if __name__ == "__main__":
    app.run(debug=True)
