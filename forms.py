# forms.py

# Import the FlaskForm class and the fields and validators modules
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo

# Define a class for the register form
class RegisterForm(FlaskForm):
  # Define the fields for the register form with validators
  name = StringField("Name", validators=[DataRequired()])
  email = StringField("Email", validators=[DataRequired(), Email()])
  password = PasswordField(
    "Password", validators=[DataRequired(), EqualTo("confirm", message="Passwords must match")]
  )
  confirm = PasswordField("Confirm Password")
  type = RadioField(
    "Type",
    choices=[("customer", "Customer"), ("worker", "Worker"), ("admin", "Admin")],
    validators=[DataRequired()],
  )
  submit = SubmitField("Register")

# Define a class for the login form
class LoginForm(FlaskForm):
  # Define the fields for the login form with validators
  email = StringField("Email", validators=[DataRequired(), Email()])
  password = PasswordField("Password", validators=[DataRequired()])
  submit = SubmitField("Login")
