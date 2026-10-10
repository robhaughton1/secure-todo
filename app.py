from flask import Flask, render_template

application = Flask(__name__)

@application.route('/')
def home_rediret():
    return render_template('home.html')

@application.route('/home')
def home():
    return render_template('home.html')

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    application.run(debug=True)