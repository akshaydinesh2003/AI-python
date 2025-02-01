from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from bson import ObjectId
import os

port = int(os.getenv("PORT", 4000))

app = Flask(__name__)

# MongoDB Atlas connection string
app.config["MONGO_URI"] = "mongodb+srv://21cs401:l9nLAxDG5vOggOvt@python-tutor.npzpa.mongodb.net/python-tutor?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def get_id(self):
        return self.id
    
app.config['SECRET_KEY'] ="akshay@123"

@login_manager.user_loader
def load_user(user_id):
    # Ensure `user_id` is converted to an ObjectId
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(id=str(user['_id']), username=user['username'], email=user['Email'])
    return None

# Route to register a new user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        Email = request.form['Email']
        password = request.form['password']
        
        # Check if the user already exists
        user = mongo.db.users.find_one({'Email': Email})
        if user:
            flash("User already exists. Please log in.", "error")
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into MongoDB
        new_user = {
            'username': username,
            'Email': Email,
            'password': hashed_password
        }
        mongo.db.users.insert_one(new_user)

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("signup.html")

# Route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email']
        password = request.form['password']

        # Find the user in MongoDB
        user_data = mongo.db.users.find_one({'Email': Email})

        if user_data:
            if check_password_hash(user_data['password'], password):
                # Create a User object
                user = User(id=str(user_data['_id']), username=user_data['username'], email=user_data['Email'])

                # Log the user in
                login_user(user)

                return redirect(url_for('dashboard'))

            flash("Invalid password", "error")
            return redirect(url_for('login'))

        flash("User not found", "error")
        return redirect(url_for('login'))

    return render_template("login.html")

# Route to the dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

# Route to logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
