#!/usr/bin/env python3
"""
DynoAI - Dynamic AI Assistant Application
Main Flask application entry point

This module serves as the main entry point for the DynoAI application,
initializing all components and starting the web server.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_socketio import SocketIO

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application components
from config import get_config
from web.routes import routes_bp, initialize_routes
from web.websocket import create_socketio, initialize_websocket
from ai.core import initialize_ai_engine
from ai.memory import initialize_memory_system
from ai.plugins import initialize_plugin_system
from utils.helpers import ensure_directories, setup_logging, get_system_info

# Global variables
app = None
socketio = None
config = None

def create_app(config_name=None):
    """
    Create and configure the Flask application
    
    Args:
        config_name (str, optional): Configuration environment name
        
    Returns:
        Flask: Configured Flask application
    """
    global app, config
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize configuration with app
    config.init_app(app)
    
    # Setup logging
    setup_logging(app.config.get('LOG_LEVEL', 'INFO'))
    
    # Ensure required directories exist
    ensure_directories([
        app.config.get('DATA_DIR', 'data'),
        app.config.get('CONVERSATIONS_DIR', 'data/conversations'),
        app.config.get('MODELS_DIR', 'data/models'),
        'static/css',
        'static/js',
        'templates'
    ])
    
    # Register blueprints
    app.register_blueprint(routes_bp)
    
    # Add template globals
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config.get('APP_NAME', 'DynoAI'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'current_year': datetime.now().year,
            'debug_mode': app.config.get('DEBUG', False)
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'status_code': 404
            }), 404
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An internal server error occurred',
                'status_code': 500
            }), 500
        return render_template('index.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Access to this resource is forbidden',
                'status_code': 403
            }), 403
        return render_template('index.html'), 403
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            system_info = get_system_info()
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': app.config.get('APP_VERSION', '1.0.0'),
                'environment': app.config.get('ENV', 'development'),
                'system': system_info
            })
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500
    
    # Main route
    @app.route('/')
    def index():
        """Main application route"""
        return render_template('index.html')
    
    # Chat interface route
    @app.route('/chat')
    def chat():
        """Chat interface route"""
        return render_template('chat.html')
    
    return app

def initialize_components(app_instance):
    """
    Initialize all application components
    
    Args:
        app_instance (Flask): Flask application instance
        
    Returns:
        bool: True if all components initialized successfully
    """
    try:
        logging.info("Initializing DynoAI components...")
        
        # Initialize AI engine
        if not initialize_ai_engine(app_instance.config):
            logging.error("Failed to initialize AI engine")
            return False
        logging.info("✓ AI engine initialized")
        
        # Initialize memory system
        if not initialize_memory_system(app_instance.config):
            logging.error("Failed to initialize memory system")
            return False
        logging.info("✓ Memory system initialized")
        
        # Initialize plugin system
        if not initialize_plugin_system(app_instance.config):
            logging.error("Failed to initialize plugin system")
            return False
        logging.info("✓ Plugin system initialized")
        
        # Initialize web routes
        if not initialize_routes(app_instance.config):
            logging.error("Failed to initialize web routes")
            return False
        logging.info("✓ Web routes initialized")
        
        # Initialize WebSocket functionality
        if not initialize_websocket(app_instance, app_instance.config):
            logging.error("Failed to initialize WebSocket functionality")
            return False
        logging.info("✓ WebSocket functionality initialized")
        
        logging.info("All components initialized successfully!")
        return True
        
    except Exception as e:
        logging.error(f"Component initialization failed: {e}")
        return False

def create_socketio_app(app_instance):
    """
    Create and configure SocketIO instance
    
    Args:
        app_instance (Flask): Flask application instance
        
    Returns:
        SocketIO: Configured SocketIO instance
    """
    global socketio
    
    try:
        socketio = create_socketio(app_instance)
        logging.info("SocketIO instance created successfully")
        return socketio
    except Exception as e:
        logging.error(f"Failed to create SocketIO instance: {e}")
        return None

def run_app(host=None, port=None, debug=None):
    """
    Run the Flask application
    
    Args:
        host (str, optional): Host to bind to
        port (int, optional): Port to bind to
        debug (bool, optional): Debug mode
    """
    global app, socketio, config
    
    if not app or not socketio:
        logging.error("Application not properly initialized")
        return
    
    # Use config defaults if not specified
    host = host or config.HOST
    port = port or config.PORT
    debug = debug if debug is not None else config.DEBUG
    
    logging.info(f"Starting DynoAI server on {host}:{port}")
    logging.info(f"Debug mode: {debug}")
    logging.info(f"Environment: {config.ENV}")
    
    try:
        # Run with SocketIO support
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True  # For development
        )
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server stopped")

def main():
    """Main application entry point"""
    try:
        # Print startup banner
        print("=" * 60)
        print("🤖 DynoAI - Dynamic AI Assistant Application")
        print("=" * 60)
        
        # Create Flask application
        app_instance = create_app()
        
        # Initialize all components
        if not initialize_components(app_instance):
            print("❌ Failed to initialize application components")
            sys.exit(1)
        
        # Create SocketIO instance
        socketio_instance = create_socketio_app(app_instance)
        if not socketio_instance:
            print("❌ Failed to create SocketIO instance")
            sys.exit(1)
        
        print("✅ Application initialized successfully!")
        print(f"🌐 Access the application at: http://{app_instance.config['HOST']}:{app_instance.config['PORT']}")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the application
        run_app()
        
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        print(f"❌ Application startup failed: {e}")
        sys.exit(1)

# Development server configuration
if __name__ == '__main__':
    # Handle command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='DynoAI - Dynamic AI Assistant')
    parser.add_argument('--host', default=None, help='Host to bind to')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--config', default=None, help='Configuration environment')
    
    args = parser.parse_args()
    
    # Create application with specified config
    app = create_app(args.config)
    
    # Initialize components
    if not initialize_components(app):
        print("❌ Failed to initialize application components")
        sys.exit(1)
    
    # Create SocketIO instance
    socketio = create_socketio_app(app)
    if not socketio:
        print("❌ Failed to create SocketIO instance")
        sys.exit(1)
    
    # Run with command line arguments
    run_app(
        host=args.host,
        port=args.port,
        debug=args.debug
    )