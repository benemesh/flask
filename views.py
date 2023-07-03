# views.py

# Import the Flask framework and the Blueprint class
from flask import Flask, Blueprint, render_template, request, jsonify, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user

# Import the models and forms modules
from models import db, User, Role, Product, Service, Invoice, InvoiceItem, Rental
from forms import RegisterForm, LoginForm

# Create an instance of the Blueprint class
main = Blueprint("main", __name__)

# Define a route for the home page
@main.route("/")
def index():
  # Render the index.html template with the title argument
  return render_template("index.html", title="Home")

# Define a route for the products page
@main.route("/products")
def products():
  # Get all products from the database
  products = Product.query.all()

  # Render the products.html template with the title and products arguments
  return render_template("products.html", title="Products", products=products)

# Define a route for the services page
@main.route("/services", methods=["GET", "POST"])
def services():
  # Get all services from the database
  services = Service.query.all()

  # Render the services.html template with the title and services arguments
  return render_template("services.html", title="Services", services=services)

# Define a route for the about page
@main.route("/about", methods=["GET", "POST"])
def about():
  # Render the about.html template with the title argument
  return render_template("about.html", title="About")

# Define a route for the contact page
@main.route("/contact")
def contact():
  # Render the contact.html template with the title argument
  return render_template("contact.html", title="Contact")

# Define a route for the register page with GET and POST methods
@main.route("/register", methods=["GET", "POST"])
def register():
  # Create an instance of the RegisterForm class
  form = RegisterForm()

  # Check if the form is submitted and validated
  if form.validate_on_submit():
    # Get the form data from the request object
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    type = request.form.get("type")

    # Check if the email already exists in the database
    user = User.query.filter_by(email=email).first()
    if user:
      # Show an error message and redirect to the register page
      flash("Email already exists.")
      return redirect(url_for("main.register"))

    # Create a new user object with the form data
    user = User(name=name, email=email, password=password)

    # Get the role object from the database by the type name
    role = Role.query.filter_by(name=type).first()

    # Check if the role exists in the database
    if role:
      # Add the role to the user object
      user.roles.append(role)
    else:
      # Show an error message and redirect to the register page
      flash("Invalid type.")
      return redirect(url_for("main.register"))

    # Add and commit the user object to the database
    db.session.add(user)
    db.session.commit()

    # Show a success message and redirect to the login page
    flash("You have registered successfully.")
    return redirect(url_for("main.login"))

  # Render the register.html template with the title and form arguments
  return render_template("register.html", title="Register", form=form)


@main.route('/logo.png')
def logo():
    return send_from_directory('static/images', 'logo.png')
# Define a route for the login page with GET and POST methods
@main.route("/login", methods=["GET", "POST"])

def login():
  # Create an instance of the LoginForm class
  form = LoginForm()

  # Check if the form is submitted and validated
  if form.validate_on_submit():
    print('uuuuuuuuuuuuuuuusadasd')
    # Get the form data from the request object
    email = request.form.get("email")
    password = request.form.get("password")

    # Get the user object from the database by the email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    if user and user.password == password:
      # Log in the user and redirect to the profile page
      login_user(user)
      return redirect(url_for("main.profile"))
    else:
      # Show an error message and redirect to the login page
      flash("Invalid email or password.")
      return redirect(url_for("main.login"))

  # Render the login.html template with the title and form arguments
  return render_template("login.html", title="Login", form=form)

# Define a route for the logout page
@main.route("/logout")
@login_required
def logout():
  # Log out the current user and redirect to the home page
  logout_user()
  return redirect(url_for("main.index"))

# Define a route for the profile page
@main.route("/profile")
@login_required
def profile():
  # Render the profile.html template with the title argument
  return render_template("profile.html", title="Profile")

# Define a route for the manage page
@main.route("/manage")
@login_required
def manage():
  # Check if the current user is an admin
  if current_user.has_role("admin"):
    # Render the manage.html template with the title argument
    return render_template("manage.html", title="Manage")
  else:
    # Show an error message and redirect to the home page
    flash("You are not authorized to access this page.")
    return redirect(url_for("main.index"))
