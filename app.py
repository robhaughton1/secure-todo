from flask import Flask, render_template, request

application = Flask(__name__)

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
            return render_template('login.html', error = 'Invalid username or password.'), 400

        if len(username) > 16 or len(password) > 16:
            return render_template('login.html', error = 'Username or password cannot exceed 16 characters.'), 400      

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
            return render_template('register.html', error = 'Invalid username or password.'), 400

        if len(username) > 16 or len(password) > 16:
            return render_template('register.html', error = 'Username or password cannot exceed 16 characters.'), 400

        return render_template('home.html', username = username)
    return render_template('register.html')

if __name__ == '__main__':
    application.run(debug=True)