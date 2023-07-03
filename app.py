# app.py

# Import the Flask framework and the extensions
from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_assets import Environment, Bundle

# Import the Blueprint modules
from views import main
from models import db, User

# Create an instance of the Flask app
app = Flask(__name__, static_folder='static')

# Configure the app with the secret key and the database URI
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database and the migration engine with the app
db.init_app(app)
migrate = Migrate(app, db)

# Initialize the login manager with the app
login_manager = LoginManager()
login_manager.init_app(app)

# Define a user loader function for the login manager
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# Initialize the assets extension with the app
assets = Environment(app)

# Define the bundles for the CSS and JavaScript files
css = Bundle("style.css", output="gen/style.css")
js = Bundle("script.js", output="gen/script.js")

# Register the bundles with the assets extension
assets.register("css", css)
assets.register("js", js)

# Register the Blueprint modules with the app
app.register_blueprint(main)

# Run the app if this file is executed as the main program
if __name__ == "__main__":
  app.run(debug=True)
