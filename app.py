from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson import ObjectId
import requests
import json
import requests
from aiint import generate_ai_response 

# Gemini API Key
GEMINI_API_KEY = 'AIzaSyCBqDLJaIcPjbyoHyb2FfXxeX99Mmq_XSE'
GEMINI_API_URL = 'https://api.gemini.com/v1/generate'

# Flask App Configuration
app = Flask(__name__)
app.secret_key = 'akshay@123'
app.config["MONGO_URI"] = "mongodb+srv://21cs401:l9nLAxDG5vOggOvt@python-tutor.npzpa.mongodb.net/python-tutor?retryWrites=true&w=majority"

# Initialize Flask Extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Routes


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
            'password': hashed_password,
            'progress': 0,
            'age': 'default',
            'experience': 'beginner'
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
            session['user_id'] = str(user_data['_id'])  # Store the user id in session
            flash('Login successful!', 'success')

            # Redirect to dashboard or age/experience page if not set
            if 'age' not in user_data or 'experience' not in user_data:
                return redirect(url_for('age_experience'))
            
            return redirect(url_for('dashboard'))  # Redirect to the dashboard or home page
        else:
            flash('Invalid login credentials. Please try again.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Age and Experience Route (for new users)
@app.route('/age-experience', methods=['GET', 'POST'])
def age_experience():
    if request.method == 'POST':
        age = request.form['age']
        experience = request.form['experience']

        # Update the user's age and experience level in the database
        mongo.db.users.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"age": age, "experience": experience}}
        )

        return redirect(url_for('dashboard'))

    return render_template('age_experience.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    user_data = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    progress = user_data['progress']
    experience = user_data['experience']
    age = user_data['age']

    roadmap = call_roadmap_api(age, experience)
    return render_template('dashboard.html', roadmap=roadmap, user_progress=progress)

# Route for generating roadmap
@app.route('/generate-roadmap', methods=['POST', 'GET'])
def generate_roadmap():
    user_data = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    experience = user_data['experience']
    age = user_data['age']

    roadmap = call_roadmap_api(age, experience)
    user_progress = user_data['progress']

    return render_template('roadmap.html', roadmap=roadmap, user_progress=user_progress)

# Lesson Route
# Lesson Route
@app.route('/lesson/<int:lesson_index>', methods=['GET', 'POST'])
def lesson(lesson_index):
    user_data = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    roadmap = call_roadmap_api(age=user_data['age'], experience=user_data['experience'])

    if lesson_index < 0 or lesson_index >= len(roadmap):
        return redirect(url_for('generate_roadmap'))

    lesson_title = roadmap[lesson_index]
    lesson_content, question = get_lesson_content(lesson_index)

    ai_explanation = get_ai_tutoring(user_data['age'], user_data['experience'], lesson_content)

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = question['answer']

        if user_answer == correct_answer:
            mongo.db.users.update_one(
                {"_id": ObjectId(session['user_id'])},
                {"$set": {"progress": lesson_index + 1}}
            )
            flash("Correct answer! Progress updated.", "success")
        else:
            flash("Incorrect answer. Check the recommendations.", "danger")

        return render_template('lesson.html', lesson_title=lesson_title, lesson_content=ai_explanation, question=question, lesson_index=lesson_index)

    return render_template('lesson.html', lesson_title=lesson_title, lesson_content=ai_explanation, question=question, lesson_index=lesson_index)

# Function to generate AI tutoring content with Gemini API
# Import the function from aiint.py

# Function to generate AI tutoring content with Gemini API
def get_ai_tutoring(age, experience_level, current_lesson):
    # Construct a prompt to send to aiint.py
    prompt = f"Age: {age}, Experience Level: {experience_level}, Current Lesson: {current_lesson}"
    
    # Call generate_ai_response from aiint.py
    try:
        lesson_content = generate_ai_response(prompt)
        
        # Split the lesson content into paragraphs based on periods or other markers.
        paragraphs = lesson_content.split('. ')
        
        # Trim any extra whitespace and add a period to the end of each paragraph
        paragraphs = [p.strip() + '.' if not p.endswith('.') else p.strip() for p in paragraphs]
        
        return paragraphs  # Return a list of paragraphs
    except Exception as e:
        print(f"Error in AI tutoring generation: {e}")
        return ["Error generating lesson content. Please try again later."]



# Function to retrieve lesson content and questions
def get_lesson_content(lesson_index):
    lessons = [
        ("Lesson 1: Basics of Python", "Explain how Python works with variables and data types.", "What is the output of print(2 + 3)?", "5"),
        ("Lesson 2: Variables & Data Types", "Learn about the different data types in Python.", "What is the data type of the value 'Hello'?", "String"),
        ("Lesson 3: Conditional Statements", "Learn how to use if, elif, and else statements.", "What is the output of if 3 > 2: print('Yes')?", "Yes"),
    ]
    
    lesson_content = lessons[lesson_index][1]
    question = {
        'question': lessons[lesson_index][2],
        'answer': lessons[lesson_index][3]
    }
    
    return lesson_content, question

# Function to generate the roadmap based on user experience
def call_roadmap_api(age, experience):
    roadmap = {
        "beginner": [
            "Lesson 1: Basics of Python",
            "Lesson 2: Variables & Data Types",
            "Lesson 3: Conditional Statements",
            "Lesson 4: Loops",
            "Lesson 5: Functions",
            "Lesson 6: Lists and Tuples",
            "Lesson 7: Dictionaries",
            "Lesson 8: Exception Handling",
            "Lesson 9: File Handling",
        ],
        "intermediate": [
            "Lesson 1: Advanced Loops",
            "Lesson 2: List Comprehensions",
            "Lesson 3: Recursion",
            "Lesson 4: Object-Oriented Programming",
            "Lesson 5: Modules and Packages",
            "Lesson 6: File I/O Operations",
            "Lesson 7: Regular Expressions",
            "Lesson 8: Working with APIs",
            "Lesson 9: Introduction to Databases",
        ],
        "advanced": [
            "Lesson 1: Basics of NumPy",
            "Lesson 2: Data Manipulation with Pandas",
            "Lesson 3: Data Visualization with Matplotlib",
            "Lesson 4: Machine Learning Basics",
            "Lesson 5: Advanced ML Algorithms",
            "Lesson 6: Introduction to Neural Networks",
            "Lesson 7: Deep Learning with TensorFlow",
            "Lesson 8: Natural Language Processing",
            "Lesson 9: Building AI Projects",
        ],
    }
    return roadmap.get(experience, roadmap["beginner"])

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
