from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson import ObjectId
import requests
import json
import requests
from aiint import generate_ai_response 

GEMINI_API_KEY = 'AIzaSyCBqDLJaIcPjbyoHyb2FfXxeX99Mmq_XSE'
GEMINI_API_URL = 'https://api.gemini.com/v1/generate'


app = Flask(__name__)
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
@app.route('/lesson/<int:lesson_index>', methods=['GET', 'POST'])
def lesson(lesson_index):
    user_data = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    experience = user_data['experience']
    roadmap = call_roadmap_api(age=user_data['age'], experience=experience)

    try:
        lesson_content, question = get_lesson_content(lesson_index)

        ai_explanation = get_ai_tutoring(user_data['age'], user_data['experience'], lesson_content)

        if request.method == 'POST':
            user_answer = request.form.get('answer')
            correct_answer = question['answer']

            if user_answer.strip() == correct_answer:
                mongo.db.users.update_one(
                    {"_id": ObjectId(session['user_id'])},
                    {"$set": {"progress": lesson_index + 1}}
                )
                flash("Correct answer! Progress updated.", "success")

                if lesson_index + 1 < len(roadmap):
                    return redirect(url_for('lesson', lesson_index=lesson_index + 1))
                else:
                    if experience == "beginner":
                        mongo.db.users.update_one(
                            {"_id": ObjectId(session['user_id'])},
                            {"$set": {"experience": "intermediate", "progress": 0}}
                        )
                        flash("Congratulations! You've completed the beginner roadmap and advanced to intermediate.", "success")
                    return redirect(url_for('generate_roadmap'))

            else:
                flash("Incorrect answer. Check the recommendations.", "danger")

        return render_template('lesson.html', lesson_title=roadmap[lesson_index], 
                               lesson_content=ai_explanation, question=question, 
                               lesson_index=lesson_index)
    except IndexError:
        flash("Invalid lesson index. Redirecting to dashboard.", "danger")
        return redirect(url_for('dashboard'))

# Function to generate AI tutoring content with Gemini API
def get_ai_tutoring(age, experience_level, current_lesson):
    prompt = f"Age: {age}, Experience Level: {experience_level}, Current Lesson: {current_lesson}"
    
    try:
        lesson_content = generate_ai_response(prompt)
        
        paragraphs = lesson_content.split('. ')
        paragraphs = [p.strip() + '.' if not p.endswith('.') else p.strip() for p in paragraphs]
        
        return paragraphs 
    except Exception as e:
        print(f"Error in AI tutoring generation: {e}")
        return ["Error generating lesson content. Please try again later."]




# Function to retrieve lesson content and questions
# Lesson content for different levels
lessons_content = {
    "beginner": {
        "Lesson 1: Basics of Python": ("Explain how Python works with variables and data types.", "What is the output of print(2 + 3)?", "5"),
        "Lesson 2: Variables & Data Types": ("Learn about the different data types in Python.", "What is the data type of the value 'Hello'?", "String"),
        "Lesson 3: Conditional Statements": ("Learn how to use if, elif, and else statements.", "What is the output of if 3 > 2: print('Yes')?", "Yes"),
        "Lesson 4: Loops": ("Learn how to use for and while loops.", "What is the output of: for i in range(3): print(i)?", "2"),
        "Lesson 5: Functions": ("Learn how to define and call functions in Python.", "What is the keyword used to define a function in Python?", "def"),
        "Lesson 6: Lists and Tuples": ("Learn about list and tuple operations.", "What is the output of: len([1, 2, 3])?", "3"),
        "Lesson 7: Dictionaries": ("Learn about Python dictionaries.", "What is the output of: {'a': 1, 'b': 2}['b']?", "2"),
        "Lesson 8: Exception Handling": ("Learn how to handle exceptions using try-except blocks.", "What keyword is used to handle exceptions in Python?", "except"),
        "Lesson 9: File Handling": ("Learn how to work with files in Python.", "What method is used to read the content of a file?", "read"),
    },
    "intermediate": {
        "Lesson 1: Advanced Loops": ("Learn about advanced loop concepts.", "What is the output of: for i in range(3, 6): print(i)?", "3\n4\n5"),
        "Lesson 2: List Comprehensions": ("Understand how to create lists using list comprehensions.", "What is the output of: [x**2 for x in range(3)]?", "[0, 1, 4]"),
        "Lesson 3: Recursion": ("Learn about recursion and how functions can call themselves.", "What is the base case in recursion?", "Condition to stop recursion"),
        "Lesson 4: Object-Oriented Programming": ("Learn about classes and objects in Python.", "What keyword is used to define a class?", "class"),
        "Lesson 5: Modules and Packages": ("Learn how to use and create modules.", "What is the file extension for Python modules?", ".py"),
        "Lesson 6: File I/O Operations": ("Learn about advanced file handling.", "What method is used to append content to a file?", "write"),
        "Lesson 7: Regular Expressions": ("Learn about regular expressions and pattern matching.", "What library in Python is used for regex?", "re"),
        "Lesson 8: Working with APIs": ("Learn how to interact with APIs.", "Which library is commonly used for API requests?", "requests"),
        "Lesson 9: Introduction to Databases": ("Learn basic database operations using Python.", "What library is used to interact with SQLite in Python?", "sqlite3"),
    },
    "advanced": {
        "Lesson 1: Basics of NumPy": ("Learn the basics of NumPy for numerical computing.", "What is the main object of NumPy?", "ndarray"),
        "Lesson 2: Data Manipulation with Pandas": ("Learn how to manipulate data using Pandas.", "What method is used to read a CSV file in Pandas?", "read_csv"),
        "Lesson 3: Data Visualization with Matplotlib": ("Learn how to create plots using Matplotlib.", "What function is used to plot data in Matplotlib?", "plot"),
        "Lesson 4: Machine Learning Basics": ("Learn the basics of machine learning.", "What is the primary library for machine learning in Python?", "scikit-learn"),
        "Lesson 5: Advanced ML Algorithms": ("Understand advanced ML algorithms.", "Name an ensemble learning method.", "Random Forest"),
        "Lesson 6: Introduction to Neural Networks": ("Learn the basics of neural networks.", "What is the function of an activation layer?", "Non-linear transformation"),
        "Lesson 7: Deep Learning with TensorFlow": ("Learn about deep learning using TensorFlow.", "What is TensorFlow primarily used for?", "Deep learning"),
        "Lesson 8: Natural Language Processing": ("Learn the basics of NLP.", "What library is commonly used for NLP in Python?", "NLTK"),
        "Lesson 9: Building AI Projects": ("Understand how to combine all concepts to build AI projects.", "What is the first step in building an AI project?", "Problem definition"),
    },
}

# Function to get lesson content dynamically
def get_lesson_content(lesson_index):
    user_data = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    experience = user_data['experience']
    
    lessons = lessons_content.get(experience, {})
    
    lessons_list = list(lessons.items())
    
    if 0 <= lesson_index < len(lessons_list):
        lesson_title, (content, question, answer) = lessons_list[lesson_index]
        return (content, {"question": question, "answer": answer})
    else:
        raise IndexError("Invalid lesson index")



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
