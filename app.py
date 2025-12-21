from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from routes import register_routes

app = Flask(__name__)

# Choose the appropriate configuration
# For normal development:
app.config.from_object(DevelopmentConfig)

# For testing (optional override):
# app.config.from_object(TestingConfig)

# For production:
# app.config.from_object(ProductionConfig)

# Register your routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])
