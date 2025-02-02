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


user_progress = 0

@app.route('/generate-roadmap', methods=['POST', 'GET'])
def generate_roadmap():
    age = request.form.get('age', 'default_age')  # Provide a default value
    experience = request.form.get('experience', 'beginner')  # Provide a default value

    # Call the API to generate the roadmap based on age and experience
    api_response = call_roadmap_api(age, experience)

    # Ensure `api_response` is a list or dict that can be iterated
    if not api_response:
        api_response = []

    return render_template('roadmap.html', roadmap=api_response, user_progress=user_progress)


@app.route('/lesson/<int:lesson_index>', methods=['GET', 'POST'])
def lesson(lesson_index):
    print(f"Accessing lesson {lesson_index}")  # Debugging output
    roadmap = call_roadmap_api(age='default_age', experience='default_experience')

    if lesson_index < 0 or lesson_index >= len(roadmap):
        print("Invalid lesson index")  # Debugging output
        return redirect(url_for('generate_roadmap'))

    lesson_content, question = get_lesson_content(lesson_index)
    print(f"Lesson content: {lesson_content}, Question: {question}")  # Debugging output

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = question['answer']
        print(f"User answer: {user_answer}, Correct answer: {correct_answer}")  # Debugging output

        if user_answer == correct_answer:
            global user_progress
            user_progress = lesson_index + 1
            return redirect(url_for('generate_roadmap'))

    return render_template(
        'lesson.html',
        lesson_content=lesson_content,
        question=question,
        lesson_index=lesson_index
    )


def get_lesson_content(lesson_index):
    # Mock AI API response for lesson content and question
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

def call_roadmap_api(age, experience):
    roadmap = {
        "beginner": [
            "Lesson 1: Basics of Python", 
            "Lesson 2: Variables & Data Types", 
            "Lesson 3: Conditional Statements"
        ],
        "intermediate": [
            "Lesson 4: Functions", 
            "Lesson 5: Loops", 
            "Lesson 6: Object-Oriented Programming"
        ],
        "advanced": [
            "Lesson 7: Machine Learning Intro", 
            "Lesson 8: Deep Learning", 
            "Lesson 9: AI Projects"
        ]
    }
    return roadmap.get(experience, roadmap["beginner"])  # Default to beginner




@app.route('/logout')
def logout():
    # Perform any logout actions here
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(debug=True)
