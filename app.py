import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask application and load environment variables from the .env file
application = Flask(__name__)
load_dotenv()

application.secret_key = os.environ['SECRET_KEY']  # Use the secret key for session management and security features in Flask
if not application.secret_key:
    raise KeyError("No SECRET_KEY set for Flask application. Please set it within the appropriate file.")

# Configure the SQLAlchemy database URI to use a SQLite database named 'secure_todo.db' 
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_todo.db'
database = SQLAlchemy(application)

# Makes the database schema for the User model, which includes an id, username, and password_hash. The username is unique and cannot be null, while the password_hash isnt unique but also cannot be null. The id is the primary key for the User model.
class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(16), unique=True, nullable=False)
    password_hash = database.Column(database.String(255), nullable=False)

DUMMY_HASH = generate_password_hash('random-dummy-password-hash')  # Generate a dummy hash for timing attack prevention

# Home route logic, rendering the home.html template.
@application.route('/')
def home_redirect():
    return render_template('home.html')

# Home route logic, rendering the home.html template.
@application.route('/home')
def home():
    return render_template('home.html')

# About route logic, rendering the about.html template
@application.route('/about')
def about():
    return render_template('about.html')

# Login route logic, containing parameters for username and password and rendering the login.html template
@application.route('/login', methods = ['GET', 'POST'])
def login():

    # Checks if the request method is POST, retrieves the username and password from the form, prints the username to the console, and renders the home.html template with the username. If the request method is GET, it simply renders the login.html template.
    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Input validation for username and password, renders login.html with an error message if empty or invalid
        if not username or not password:
            return render_template('login.html', error = 'Invalid username or password.'), 200
        
        # Check if the username or password exceeds 16 or 32 characters, renders login.html with an error message if it does
        if len(username) > 16:
            return render_template('login.html', error='Username cannot exceed 16 characters.'), 200

        if len(password) > 32:
            return render_template('login.html', error='Password cannot exceed 32 characters.'), 200
        
        # Query the database for the user with the provided username
        user = database.session.scalar(
                database.select(User).where(User.username == username))

        # Check if the user exists and validate the password using the check_password_hash function. If the user does not exist, use a dummy hash to prevent timing attacks.
        if not user:
            password_valid = check_password_hash(DUMMY_HASH, password)
        else:
            password_valid = check_password_hash(user.password_hash, password)

        # If the user does not exist or the password is invalid, render the login.html template with an error message and a 401 status code
        if not user or not password_valid:
            return render_template('login.html', error='Invalid username or password.'), 401

        return render_template('home.html', username = username)
    return render_template('login.html')

# Register route logic, rendering the register.html template
@application.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Input validation for username and password, renders register.html with an error message if empty or invalid
        if not username or not password:
            return render_template('register.html', error = 'Invalid username or password.'), 200

        # Check if the username or password exceeds 16 or 32 characters, renders register.html with an error message if it does
        if len(username) > 16:
            return render_template('register.html', error = 'Username cannot exceed 16 characters.'), 200

        if len(password) > 32:
            return render_template('register.html', error = 'Password cannot exceed 32 characters.'), 200

        # Check if the username already exists in the database
        existing_user = database.session.scalar(
                database.select(User).where(User.username == username))

        # If the username already exists, render register.html with an error message and a 409 status code
        if existing_user:
            return render_template('register.html', error = 'Username is unavailable.'), 409

        # Makes the password more secure by hashing it before storing it in the database
        password_hash = generate_password_hash(password)

        # Create a new user instance with the provided username and hashed password
        new_user = User(
                username=username,
                password_hash=password_hash)
          
        # Add the new user to the database session and commit the changes to save it in the database
        database.session.add(new_user)
        database.session.commit()

        # Finally, render the home.html template with the username after successful registration
        return render_template('home.html', username = username)
    return render_template('register.html')

# Run the application in debug mode and create the database tables if they don't exist
if __name__ == '__main__':
    with application.app_context():
        database.create_all()  # Create the database tables if they don't exist

    application.run(debug=True)
