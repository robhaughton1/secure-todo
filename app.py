import os
import hmac
import hashlib
import redis
import requests
import secrets
from redis.exceptions import RedisError
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Flask application and load environment variables from the .env file
application = Flask(__name__)
load_dotenv()

# Configure Flask-Limiter for rate limiting to prevent abuse and brute-force attacks. It uses Redis as the storage backend to keep track of request counts and enforce limits based on the client's IP address.
limiter = Limiter(
    key_func=get_remote_address,
    app=application,
    storage_uri=os.environ.get(
    "REDIS_URL",
    "redis://127.0.0.1:6379/0"
    )       
)

application.secret_key = os.environ['SECRET_KEY']  # Use the secret key for session management and security features in Flask
if not application.secret_key:
    raise KeyError("No SECRET_KEY set for Flask application. Please set it within the appropriate file.")

# Use the USERNAME_HMAC_KEY for HMAC hashing of usernames to create a unique identifier for each user. This key is used to ensure that the username identifiers are secure and cannot be easily guessed or reverse-engineered.
USERNAME_HMAC_KEY = os.environ["USERNAME_HMAC_KEY"].encode("utf-8")

# Use the TURNSTILE_SITE_KEY and TURNSTILE_SECRET_KEY for CAPTCHA verification to prevent automated login attempts and enhance security. These keys are used to integrate with the Turnstile CAPTCHA service.
TURNSTILE_SITE_KEY = os.environ["TURNSTILE_SITE_KEY"]
TURNSTILE_SECRET_KEY = os.environ["TURNSTILE_SECRET_KEY"]

# Function to generate a unique identifier for a given username using HMAC with SHA-256 hashing. This helps in securely identifying users without exposing their actual usernames.
def get_username_identifier(username):
    normalized_username = username.strip()

    return hmac.new(
        USERNAME_HMAC_KEY,
        normalized_username.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

# Function to record a failed login attempt for a specific username. It increments the count of failed attempts in Redis and sets an expiration time for the key to implement rate limiting.
def record_failed_login(username):
    identifier = get_username_identifier(username)
    key = f"fernward:failed:{identifier}"

    count = increment_failed_attempts(
        keys=[key],
        args=[900] # Set the expiration time for the key to 900 seconds (15 minutes)
    )

    return count
# Function to check if a CAPTCHA is required for a specific username based on the number of failed login attempts. If the count of failed attempts is 5 or more, it indicates that a CAPTCHA should be presented to the user.
def captcha_required(username):
    identifier = get_username_identifier(username)
    key = f"fernward:failed:{identifier}"

    count = redis_client.get(key)

    return count is not None and int(count) >= 5

# Initialize the Redis client for rate limiting and other caching purposes
redis_client = redis.Redis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"),
    decode_responses=True
)

# Redis Lua script to increment the failed login attempts for a specific username and set an expiration time for the key. This script is used to implement rate limiting for login attempts, preventing brute-force attacks by limiting the number of failed login attempts within a certain time frame.
increment_failed_attempts = redis_client.register_script("""
    local count = redis.call('INCR', KEYS[1])

    if count == 1 then
        redis.call('EXPIRE', KEYS[1], ARGV[1])
    end

    return count
""")

# Function to verify the Turnstile CAPTCHA token provided by the user during login. It sends a request to the Turnstile verification endpoint with the secret key and the user's response token, and checks if the verification was successful.
def verify_turnstile(token):
    if not token:
        return False

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": token
            },
            timeout=5
        )

        response.raise_for_status()
        result = response.json()

        return (result.get("success") is True and result.get("hostname") in {"localhost", "127.0.0.1"})

    except (requests.RequestException, ValueError):
        return False

def create_authenticated_session(user_id):
    session.clear()
    session_id = secrets.token_urlsafe(32)

    try:
        redis_client.set(
            f"fernward:session:{session_id}",
            str(user_id),
            ex=3600
        )
    except RedisError:
        application.logger.error(
            "Redis unavailable during session creation"
        )
        return False

    session["user_id"] = user_id
    session["session_id"] = session_id
    session["csrf_token"] = secrets.token_urlsafe(32)
    return True

# Configure the SQLAlchemy database URI to use a SQLite database named 'secure_todo.db' 
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///secure_todo.db'
)
database = SQLAlchemy(application)

# Makes the database schema for the User model, which includes an id, username, and password_hash. The username is unique and cannot be null, while the password_hash isnt unique but also cannot be null. The id is the primary key for the User model.
class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(16), unique=True, nullable=False)
    password_hash = database.Column(database.String(255), nullable=False)

class Task(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False, index=True)
    title = database.Column(database.String(200), nullable=False)
    completed = database.Column(database.Boolean, nullable=False, default=False)
    created_at = database.Column(database.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

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

# Login route logic, handling both GET and POST requests. The POST request is rate-limited to 10 requests per minute to prevent brute-force attacks.
@application.route('/login', methods = ['GET', 'POST'])
@limiter.limit("10 per minute", methods=["POST"])
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

        # Check if CAPTCHA is required for the username based on failed login attempts. If required, verify the Turnstile CAPTCHA token provided by the user. If the verification fails, render the login.html template with an error message and a 403 status code.
        if captcha_required(username):
            token = request.form.get("cf-turnstile-response", "")

            # If the token is not provided, render the login.html template with an error message and a 403 status code.
            if not token:
                return render_template("login.html",error="Please complete the security verification to continue.", username=username, turnstile_site_key=TURNSTILE_SITE_KEY, show_captcha=True), 403

            if not verify_turnstile(token):
                return render_template("login.html", error="CAPTCHA verification failed. Please try again.", username=username, turnstile_site_key=TURNSTILE_SITE_KEY, show_captcha=True), 403
        
        # Query the database for the user with the provided username
        user = database.session.scalar(
                database.select(User).where(User.username == username))

        # Check if the user exists and validate the password using the check_password_hash function. If the user does not exist, use a dummy hash to prevent timing attacks.
        if not user:
            password_valid = check_password_hash(DUMMY_HASH, password)
        else:
            password_valid = check_password_hash(user.password_hash, password)

        # If the user does not exist or the password is invalid, record the failed login attempt and render the login.html template with an error message and a 401 status code.
        if not user or not password_valid:
            record_failed_login(username)
            return render_template('login.html', error='Invalid username or password.', turnstile_site_key=TURNSTILE_SITE_KEY, username=username, show_captcha=captcha_required(username)), 401

        # Create an authenticated session after successful login.
        if not create_authenticated_session(user.id):
            return "Authentication service temporarily unavailable.", 503

        return redirect(url_for('dashboard'))
    return render_template('login.html', turnstile_site_key=TURNSTILE_SITE_KEY)

# Logout route logic, handling the POST request to log out the user. It deletes the session from Redis and clears the session data in Flask, then redirects to the home page.
@application.route("/logout", methods=["POST"])
def logout():
    session_id = session.get("session_id")

    if session_id:
        try:
            redis_client.delete(
                f"fernward:session:{session_id}"
            )
        except RedisError:
            application.logger.error(
                "Redis unavailable during logout"
            )
            return "Logout temporarily unavailable. Please try again.", 503

    session.clear()
    return redirect(url_for("home"))

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

        # Create an authenticated session for the newly registered user.
        if not create_authenticated_session(new_user.id):
            return "Authentication service temporarily unavailable.", 503

        return redirect(url_for('dashboard'))
    return render_template('register.html')

def authenticated_user():
    user_id = session.get("user_id")
    session_id = session.get("session_id")
    if not user_id or not session_id:
        return None, redirect(url_for("login"))
    try:
        stored_user_id = redis_client.get(f"fernward:session:{session_id}")
    except RedisError:
        application.logger.error("Redis unavailable during session validation")
        return None, ("Authentication service temporarily unavailable.", 503)
    if stored_user_id != str(user_id):
        session.clear()
        return None, redirect(url_for("login"))
    user = database.session.get(User, user_id)
    if not user:
        session.clear()
        return None, redirect(url_for("login"))
    return user, None


@application.route("/tasks", methods=["POST"])
def create_task():
    user, error = authenticated_user()
    if error is not None:
        return error
    expected_token = session.get("csrf_token", "")
    supplied_token = request.form.get("csrf_token", "")
    if not expected_token or not hmac.compare_digest(expected_token, supplied_token):
        return "Invalid request token.", 403
    title = request.form.get("title", "").strip()
    if not title or len(title) > 200:
        return "Task title must be between 1 and 200 characters.", 400
    database.session.add(Task(user_id=user.id, title=title))
    database.session.commit()
    return redirect(url_for("dashboard"), code=303)


@application.route('/dashboard')
def dashboard():
    user, error = authenticated_user()
    if error is not None:
        return error
    tasks = database.session.scalars(
        database.select(Task).where(Task.user_id == user.id).order_by(Task.id.desc())
    ).all()
    return render_template(
        'dashboard.html', username=user.username, tasks=tasks,
        csrf_token=session["csrf_token"]
    )

# Error handler for rate limit exceeded (HTTP 429)
@application.errorhandler(429)
def rate_limit_exceeded(error):
    return "Too many requests. Please try again later.", 429

@application.errorhandler(500)
def internal_server_error(error):
    application.logger.error("Internal server error", exc_info=error.original_exception or error)
    return "Service temporarily unavailable. Please try again later.", 500

# Run the application in debug mode and create the database tables if they don't exist
if __name__ == '__main__':
    with application.app_context():
        database.create_all()  # Create the database tables if they don't exist

    application.run(debug=True)
