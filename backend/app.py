from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from routes.search import search_bp
from routes.queries import query_bp
from routes.graphs import graph_bp
from routes.prefixes import prefixes_bp

# Initialize Flask application
app = Flask(__name__)

# Register the blueprint
app.register_blueprint(search_bp)
app.register_blueprint(query_bp)
app.register_blueprint(graph_bp)
app.register_blueprint(prefixes_bp)

# This is the "Magic" step to kill the Swagger 2.0 conflict
swagger_template = {
    "openapi": "3.0.0",
    "info": {
        "title": "GraphDB Web UI Clone API",
        "version": "1.0.0",
    },
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

app.config["SWAGGER"] = {
    "title": "GraphDB Web UI Clone API",
    "uiversion": 3,
    "openapi": "3.0.0",
}

swagger = Swagger(
    app, config=swagger_config, template=swagger_template, template_file="swagger.yaml"
)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost",
                "http://localhost:4200",  # React default dev port
                "http://127.0.0.1",
                "http://127.0.0.1:5000",  # Flask default port
            ]
        }
    },
)
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
