from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson import ObjectId
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Configure the Flask app
app.secret_key = 'akshay@123'
app.config["MONGO_URI"] = "mongodb+srv://21cs401:l9nLAxDG5vOggOvt@python-tutor.npzpa.mongodb.net/python-tutor?retryWrites=true&w=majority"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)


@app.route('/')
def home():
    return render_template('home.html')


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password before saving it to the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Check if email already exists
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))
        
        # Insert new user into the database
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })
        
        flash('Signup successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find the user by email
        user_data = mongo.db.users.find_one({"email": email})
        
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            flash('Login successful!', 'success')
            # You can create a session or perform any other actions here
            return redirect(url_for('dashboard'))  # Redirect to the dashboard or home page
        else:
            flash('Invalid login credentials. Please try again.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


# Dashboard Route (or any page after login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    # Perform any logout actions here
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(debug=True)
