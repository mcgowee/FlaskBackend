from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Load configuration
    app.config.from_object('app.config.Config')

    # Register blueprints
    from app.routes import bp as local_bp
    from app.OpenAI1 import bp_openai as openai_bp
    from app.langchain_routes import bp_langchain as langchain_bp
    from app.LocalLLMApp import bp_pandasai as pandasai_bp

    app.register_blueprint(local_bp, url_prefix='/')
    app.register_blueprint(openai_bp, url_prefix='/')
    app.register_blueprint(langchain_bp, url_prefix='/')
    app.register_blueprint(pandasai_bp, url_prefix='/')

    return app
