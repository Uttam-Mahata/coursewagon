import requests
import os # Import os library
from flask import Flask
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from extensions import db
from routes.course_routes import course_bp
from routes.auth_routes import auth_bp
from config import Config

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Set TZ environment variable before creating the scheduler
os.environ['TZ'] = 'UTC'
app = Flask(__name__)
scheduler = APScheduler()

# Update CORS configuration
CORS(app,
     resources={r"/*": {
         "origins": [
             "http://localhost:4200"
         ],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }}
)

app.config.from_object(Config)

app.config.update(
    SCHEDULER_API_ENABLED=True,
    SCHEDULER_TIMEZONE="UTC"
)

db.init_app(app)
scheduler.init_app(app)

jwt = JWTManager(app)

def keep_alive():
    """
    Function to make a request to the application to keep it alive
    """
    try:
        # Replace with your actual application URL
        response = requests.get('http://localhost:5000/api/health')
        logger.info(f"Keep-alive ping sent. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Keep-alive request failed: {str(e)}")

# Add scheduled job
@scheduler.task('interval', id='keep_alive_job', minutes=15, misfire_grace_time=None)
def schedule_keep_alive():
    with app.app_context():
        keep_alive()

# Start the scheduler
scheduler.start()
# Register blueprints
app.register_blueprint(course_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/api/health')
def health_check():
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)