from flask import Flask
from routes import register_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_with_a_secret_key'

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
