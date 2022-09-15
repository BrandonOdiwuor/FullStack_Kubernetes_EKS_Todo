import logging
from flask import Flask, jsonify
from flask_cors import CORS

from app.auth import AuthError

def create_app():
    app = Flask(__name__)

    if __name__ != '__main__':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    CORS(app)

    # Register blueprints
    from app.todo import todo as todo_blueprint
    app.register_blueprint(todo_blueprint)

    @app.route("/healthz")
    def heath_endpoint():
        response = jsonify({'message': 'Healthy'})
        response.status_code = 200
        return response 

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    return app