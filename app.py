
# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import inspect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app) # call db.init_app(app) here
    return app
db = SQLAlchemy()
app = create_app()
bcrypt = Bcrypt(app)
 # do not give app to db
migrate = Migrate(app, db) # initialize migrate with app and db



# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# define your models here

# In the app.py file
# In the app.py file
from flask_wtf import FlaskForm
from wtforms import SelectField

# The rest of the code as before

from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    section_id = SelectField('Section ID', validators=[DataRequired()], coerce=int)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.section_id.choices = [(section.id, section.name) for section in Section.query.all()]

    submit = SubmitField('Submit')

    # Add an id attribute to store the user id
    id = None

    # Custom validator to check if the username is unique
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != self.id:
            raise ValidationError('This username is already taken.')

    # Custom validator to check if the email is unique
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.id:
            raise ValidationError('This email is already taken.')

    # Custom validator to check if the section id is valid
    def validate_section_id(self, section_id):
        section = Section.query.get(section_id.data)
        if not section:
            raise ValidationError('This section id does not exist.')


# Define a route for the users page
@app.route('/users')
@login_required
def users():
    # Get all the users from the database
    users = User.query.all()
    return render_template('users.html', users=users)

# Define a route for adding a new user
# Define a route for adding a new user
@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    # Create a form instance
    form = UserForm()
    if form.validate_on_submit():
        # Create a new user object with the form data
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            section_id=form.section_id.data,
        )
        # Set the password hash for the new user
        new_user.set_password(form.password.data)

        # Add the new user to the database and commit the changes
        db.session.add(new_user)
        db.session.commit()

        # Check if the user is the manager of the section they choose
        manager = SectionClosure.query.filter_by(ancestor=new_user.section_id, descendant=new_user.section_id, depth=0).count() == 1

        # Flash a message based on the manager status
        if manager:
            flash('User added successfully as a manager!')
        else:
            flash('User added successfully as a staff!')

        return redirect(url_for('users'))
    return render_template('add_user.html', form=form)


# Define a route for editing an existing user
@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Get the user to edit from the database or return 404 if not found
    user = User.query.get_or_404(user_id)

    # Create a form instance with the current user data
    form = UserForm(
        username=user.username,
        email=user.email,
        section_id=user.section_id,
    )

    # Set the id attribute of the form to the user id
    form.id = user.id

    # Validate the form on submission
    if form.validate_on_submit():
        # Update the user with the new data from the form
        user.username = form.username.data
        user.email = form.email.data

        # Check if the section id has changed and update it if so
        if form.section_id.data != user.section_id:
            # Get the old and new sections
            old_section = Section.query.get(user.section_id)
            new_section = Section.query.get(form.section_id.data)

            # Check if the user is the manager of their old or new sections
            old_manager = SectionClosure.query.filter_by(ancestor=user.section_id, descendant=user.section_id, depth=0).count() == 1
            new_manager = SectionClosure.query.filter_by(ancestor=form.section_id.data, descendant=form.section_id.data, depth=0).count() == 0

            # Update the section id for the user
            user.section_id = form.section_id.data

            # Flash a message based on the manager status changes
            if old_manager and not new_manager:
                flash('User updated successfully from a manager to a staff!')
            elif not old_manager and new_manager:
                flash('User updated successfully from a staff to a manager!')
            else:
                flash('User updated successfully!')

        else:
            flash('User updated successfully!')

        # Check if the password has changed and set the new password hash if so
        if form.password.data:
            user.set_password(form.password.data)

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('users'))

    return render_template('edit_user.html', form=form, user=user)


# Define a route for deleting an existing user
@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # Get the user to delete from the database or return 404 if not found
    user = User.query.get_or_404(user_id)

    # Delete the user from the database and commit the changes
    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!')
    return redirect(url_for('users'))

# Define a route for showing the children of a user based on their section
@app.route('/users/children/<int:user_id>')
@login_required
def children_user(user_id):
    # Get the user from the database or return 404 if not found
    user = User.query.get_or_404(user_id)

    # Get all the users who have sections that are descendants of the user's section 
    children = User.query.join(SectionClosure, User.section_id == SectionClosure.descendant).filter(SectionClosure.ancestor == user.section_id, SectionClosure.depth > 0).all()

    return render_template('children_user.html', user=user, children=children)

# Define a route for showing the ancestors of a user based on their section
@app.route('/users/ancestors/<int:user_id>')
@login_required
def ancestors_user(user_id):
    # Get the user from the database or return 404 if not found
    user = User.query.get_or_404(user_id)

    # Get all the users who have sections that are ancestors of the user's section 
    ancestors = User.query.join(SectionClosure, User.section_id == SectionClosure.ancestor).filter(SectionClosure.descendant == user.section_id, SectionClosure.depth > 0).all()

    return render_template('ancestors_user.html', user=user, ancestors=ancestors)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    section_id = IntegerField('Section ID', validators=[DataRequired()])
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SectionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    parent_id = IntegerField('Parent ID')
    submit = SubmitField('Submit')

    # Add an id attribute to store the section id
    id = None

    # Custom validator to check if the section name is unique
    # def validate_name(self, name):
    #     section = Section.query.filter_by(name=name.data).first()
    #     if section and section.id != self.id:
    #         raise ValidationError('This section name is already taken.')

    # Custom validator to check if the parent id is valid
    def validate_parent_id(self, parent_id):
        if parent_id.data:
            parent = Section.query.get(parent_id.data)
            if not parent:
                raise ValidationError('This parent id does not exist.')

            
# Import the UserMixin class from Flask-Login
from flask_login import UserMixin

# Define User model with UserMixin
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    section = db.relationship('Section', backref='users')
    

    def __repr__(self):
        return f'<User {self.username}>'

    # Method to set the password hash
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Method to check the password hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Define Section model
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    children = db.relationship('Section', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<Section {self.name}>'

# Define SectionClosure model
class SectionClosure(db.Model):
    ancestor = db.Column(db.Integer, db.ForeignKey('section.id'), primary_key=True)
    descendant = db.Column(db.Integer, db.ForeignKey('section.id'), primary_key=True)
    depth = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<SectionClosure {self.ancestor} {self.descendant} {self.depth}>'


@app.route('/database')
def database():
    # Get the list of tables in the database
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    # Get the columns for each table
    columns = {}
    for table in tables:
        columns[table] = [column['name'] for column in inspector.get_columns(table)]

    # Get the rows for each table
    rows = {}
    for table in tables:
        rows[table] = [dict(row) for row in db.session.execute(f'SELECT * FROM "{table}"').fetchall()]

    return render_template('database.html', tables=tables, columns=columns, rows=rows)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Define routes
@app.route('/')
def index():
    sections = Section.query.filter_by(parent_id=None).all()
    return render_template('index.html', sections=sections)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user data
        new_user_data = {
            "username": form.username.data,
            "email": form.email.data,
            "section_id": form.section_id.data,
        }
        # Set the password hash
        new_user_data["password_hash"] = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Use INSERT OR IGNORE to insert the user data
        insert_command = User.__table__.insert().prefix_with("OR IGNORE").values(new_user_data)
        db.session.execute(insert_command)
        db.session.commit()

        # Get the new user object
        new_user = User.query.filter_by(username=form.username.data).first()

        # Log in new user
        login_user(new_user)

        flash('Registration successful!')
        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists and password is correct
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get the user's section and its ancestors
    user_section = current_user.section
    section_hierarchy = Section.query.join(SectionClosure, Section.id == SectionClosure.ancestor).filter(
        SectionClosure.descendant == user_section.id,
        SectionClosure.depth > 0
    ).all()

    # Get all the sections in the user's section hierarchy
    sections = [user_section] + [section for section in section_hierarchy]

    # Get the IDs of the sections in the user's section hierarchy
    section_ids = [section.id for section in sections]

    # Get all the users who have sections in the user's section hierarchy
    users = User.query.join(SectionClosure, User.section_id == SectionClosure.descendant).filter(
        SectionClosure.ancestor == user_section.id,
        SectionClosure.depth > 0
    ).all()

    return render_template('dashboard.html', user=current_user, sections=sections, users=users)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))


@app.route('/sections')
@login_required
def sections():
    sections = Section.query.all()
    return render_template('sections.html', sections=sections)

@app.route('/sections/add', methods=['GET', 'POST'])
@login_required
def add_section():
    form = SectionForm()
    print ('add page is ')
    if form.validate_on_submit():
        # Create new section
        new_section = Section(
            name=form.name.data,
            parent_id=form.parent_id.data,
        )

        db.session.add(new_section)
        db.session.commit()

        flash('Section added successfully!')
        return redirect(url_for('sections'))
    return render_template('add_section.html', form=form)

@app.route('/sections/edit/<int:section_id>', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    # Get the section to edit
    section = Section.query.get_or_404(section_id)

    # Create a form with the current section data
    form = SectionForm(
        name=section.name,
        parent_id=section.parent_id,
    )

    # Validate the form on submission
    if form.validate_on_submit():
        # Update the section with the new data
        section.name = form.name.data
        section.parent_id = form.parent_id.data

        # Commit the changes to the database
        db.session.commit()

        flash('Section updated successfully!')
        return redirect(url_for('sections'))

    return render_template('edit_section.html', form=form, section=section)


@app.route('/sections/delete/<int:section_id>', methods=['POST'])
@login_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    db.session.delete(section)
    db.session.commit()

    flash('Section deleted successfully!')
    return redirect(url_for('sections'))

@app.route('/sections/children/<int:section_id>')
@login_required
def children_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    children = Section.query.join(SectionClosure, Section.id == SectionClosure.descendant).filter(SectionClosure.ancestor == section.id, SectionClosure.depth > 0).all()

    return render_template('children_section.html', section=section, children=children)

@app.route('/sections/ancestors/<int:section_id>')
@login_required
def ancestors_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    ancestors = Section.query.join(SectionClosure, Section.id == SectionClosure.ancestor).filter(SectionClosure.descendant == section.id, SectionClosure.depth > 0).all()

    return render_template('ancestors_section.html', section=section, ancestors=ancestors)


# Define triggers
# Define triggers
# Define triggers
from sqlalchemy import event

@event.listens_for(Section, 'after_insert')
def after_insert_section(mapper, connection, target):
    # Insert the self-relation for the new section
    connection.execute(
        SectionClosure.__table__.insert(),
        ancestor=target.id,
        descendant=target.id,
        depth=0
    )

    # Insert the relations for the new section and its ancestors
    connection.execute(
        SectionClosure.__table__.insert().from_select(
            ['ancestor', 'descendant', 'depth'],
            db.session.query(
                SectionClosure.ancestor,
                target.id,
                SectionClosure.depth + 1
            ).filter(SectionClosure.descendant == target.parent_id)
        )
    )

    # Check if the target.users list is not empty
    if target.users:
        # Insert the relation for the new user and their section
        connection.execute(
            SectionClosure.__table__.insert(),
            ancestor=target.id,
            descendant=target.users[0].id,
            depth=0
        )

from sqlalchemy import event

@event.listens_for(Section, 'after_update')
def after_update_section(mapper, connection, target):
    # Delete or update the relation for the old user and their old section
    connection.execute(
        SectionClosure.__table__.delete().where(
            SectionClosure.ancestor == target.parent_id,
            SectionClosure.descendant == target.users[0].id
        )
    )

    # Create a new relation for the new user and their new section
    connection.execute(
        SectionClosure.__table__.insert(),
        ancestor=target.id,
        descendant=target.users[0].id,
        depth=0
    )


# Run app
if __name__ == '__main__':
    app.run(debug=True)
