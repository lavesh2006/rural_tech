import json
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load users from external file
USERS_FILE = 'users.json'


def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)


users = load_users()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user_type = request.form['user_type']  # Employer or Worker

        if email in users:
            return "User already exists! Try logging in."

        users[email] = {'name': name, 'password': password, 'user_type': user_type}
        save_users(users)

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users.update(load_users())  # Refresh users from file
        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = email
            session['user_type'] = user['user_type']
            return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_type=session['user_type'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)