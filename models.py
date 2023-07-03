# models.py

# Import the SQLAlchemy extension and the declarative base class
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# Import the security extension and the mixins for user and role models
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin

# Create an instance of the SQLAlchemy extension
db = SQLAlchemy()

# Create an instance of the declarative base class
Base = declarative_base()

# Define a helper table for the many-to-many relationship between users and roles
roles_users = db.Table(
  "roles_users",
  db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
  db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)

# Define a model class for users
class User(db.Model, UserMixin):
  # Define the table name and columns for users
  __tablename__ = "user"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  email = db.Column(db.String(255), unique=True)
  password = db.Column(db.String(255), nullable=False)
  active = db.Column(db.Boolean())
  confirmed_at = db.Column(db.DateTime())

  # Define a relationship to roles with a secondary table and backref
  roles = db.relationship(
    "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
  )

  # Define a relationship to invoices with a backref
  invoices = db.relationship("Invoice", backref="user")

  # Define a relationship to rentals with a backref
  rentals = db.relationship("Rental", backref="user")

  # Define a string representation for users
  def __repr__(self):
    return f"<User {self.name}>"

# Define a model class for roles
class Role(db.Model, RoleMixin):
  # Define the table name and columns for roles
  __tablename__ = "role"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

  # Define a string representation for roles
  def __repr__(self):
    return f"<Role {self.name}>"

# Define a model class for products
class Product(db.Model):
  # Define the table name and columns for products
  __tablename__ = "product"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text(), nullable=False)
  price = db.Column(db.Float(), nullable=False)
  stock = db.Column(db.Integer(), nullable=False)

  # Define a relationship to invoice items with a backref
  invoice_items = db.relationship("InvoiceItem", backref="product")

  # Define a relationship to rentals with a backref
  rentals = db.relationship("Rental", backref="product")

  # Define a string representation for products
  def __repr__(self):
    return f"<Product {self.name}>"

# Define a model class for services
class Service(db.Model):
  # Define the table name and columns for services
  __tablename__ = "service"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text(), nullable=False)
  price = db.Column(db.Float(), nullable=False)

  # Define a relationship to invoice items with a backref
  invoice_items = db.relationship("InvoiceItem", backref="service")

  # Define a relationship to rentals with a backref
  rentals = db.relationship("Rental", backref="service")

  # Define a string representation for services
  def __repr__(self):
    return f"<Service {self.name}>"

# Define a model class for invoices
class Invoice(db.Model):
# Define the table name and columns for invoices
  __tablename__ = "invoice"
  id = db.Column(db.Integer(), primary_key=True)
  date = db.Column(db.DateTime(), nullable=False)
  total = db.Column(db.Float(), nullable=False)

  # Define a foreign key to users with a backref
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))

  # Define a relationship to invoice items with a backref
  invoice_items = db.relationship("InvoiceItem", backref="invoice")

  # Define a string representation for invoices
  def __repr__(self):
    return f"<Invoice {self.id}>"

# Define a model class for invoice items
class InvoiceItem(db.Model):
  # Define the table name and columns for invoice items
  __tablename__ = "invoice_item"
  id = db.Column(db.Integer(), primary_key=True)
  quantity = db.Column(db.Integer(), nullable=False)
  subtotal = db.Column(db.Float(), nullable=False)

  # Define a foreign key to invoices with a backref
  invoice_id = db.Column(db.Integer(), db.ForeignKey("invoice.id"))

  # Define a foreign key to products with a backref
  product_id = db.Column(db.Integer(), db.ForeignKey("product.id"))

  # Define a foreign key to services with a backref
  service_id = db.Column(db.Integer(), db.ForeignKey("service.id"))

  # Define a string representation for invoice items
  def __repr__(self):
    return f"<InvoiceItem {self.id}>"

# Define a model class for rentals
class Rental(db.Model):
  # Define the table name and columns for rentals
  __tablename__ = "rental"
  id = db.Column(db.Integer(), primary_key=True)
  start_date = db.Column(db.DateTime(), nullable=False)
  end_date = db.Column(db.DateTime(), nullable=False)
  fee = db.Column(db.Float(), nullable=False)

  # Define a foreign key to users with a backref
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))

  # Define a foreign key to products with a backref
  product_id = db.Column(db.Integer(), db.ForeignKey("product.id"))

  # Define a foreign key to services with a backref
  service_id = db.Column(db.Integer(), db.ForeignKey("service.id"))

  # Define a string representation for rentals
  def __repr__(self):
    return f"<Rental {self.id}>"
