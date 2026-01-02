from flask import Flask
from flask_session import Session
from config import DevelopmentConfig
from routes import register_routes
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# Load configuration
app.config.from_object(DevelopmentConfig)
print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])


# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)
import models

# 🔑 Required for sessions
app.secret_key = app.config['SECRET_KEY']

# Initialize Flask-Session
Session(app)

# Register routes AFTER session setup
register_routes(app)

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])