from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb
from flask_pymongo import PyMongo
import os
from werkzeug.utils import secure_filename
 

app = Flask(
    __name__,
    static_folder="../CLIENT/static/assets",  # Point Flask to the static folder
    template_folder="../CLIENT/templates"  # Point Flask to the templates folder
)

app.secret_key = 'yashu'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yashu1601'
app.config['MYSQL_DB'] = 'bitbyte'
mysql = MySQL(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/bit2byte'

mongo = PyMongo(app)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "CLIENT/static/assets")

@app.route('/h')
def home():
    cur = mysql.connection.cursor()

    # Query to get all courses along with their instructor names
    cur.execute("SELECT * FROM courses")
    
    # Fetch all courses along with instructor data
    courses = cur.fetchall()
    
    # Close the cursor
    cur.close()

    # Pass courses data to the template
    return render_template('home.html', courses=courses)

@app.route('/loginsigup')
def loginsigup():
    return render_template('loginsigup.html')

bcrypt = Bcrypt(app)

# Route to serve the HTML file
@app.route('/compiler')
def compiler():
    return render_template('compiler.html')

JDoodle_ClientID = "65ea7ffb2ad2df011b343c107d9fcabe"
JDoodle_ClientSecret = "8bff35ebdc1b006dbc6fe649de98e26b3059260a93739994e1c4489aab8f602e"

LANGUAGE_MAP = {
    'python3': 'python3',
    'java': 'java',
    'c': 'c',
    'cpp': 'cpp14'
}

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code', '')
    language = LANGUAGE_MAP.get(data.get('language'), 'python3')

    # JDoodle API payload
    payload = {
        "script": code,
        "language": language,
        "versionIndex": "0",
        "clientId": JDoodle_ClientID,
        "clientSecret": JDoodle_ClientSecret
    }

    # Call JDoodle API
    url = "https://api.jdoodle.com/v1/execute"
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to compile code"}), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Basic validations
        if not name or not email or not password or not role:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('signup'))

        # Check if email already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", [email])
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('signup'))

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert User into Database
        try:
            cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                           (name, email, hashed_password, role))
            mysql.connection.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {e}', 'danger')
        finally:
            cursor.close()

    return render_template('loginsigup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch User from Database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, password_hash, role FROM users WHERE email = %s", [email])
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user[2], password):  # Check against 'password_hash'
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[3]
            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('dashboard.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

    user_role = session.get('user_role')
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()

    if user_role == 'instructor':
        cursor.execute("SELECT * FROM courses WHERE instructor_id = %s", (user_id,))
        courses = cursor.fetchall()
        cursor.close()
        return render_template('dashboard.html', role='instructor', courses=courses)

    elif user_role == 'student':
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        cursor.close()
        return render_template('dashboard.html', role='student', courses=courses,)

    else:
        flash('Invalid role.', 'danger')
        cursor.close()
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/events', methods=['GET', 'POST'])
def events():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Basic query to fetch all events ordered by date and time
    query = 'SELECT * FROM events ORDER BY date, time'
    params = []

    # If filters are used in a POST request (from a form submission)
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        venue = request.form.get('venue')
        organizer = request.form.get('organizer')

        # Add filtering conditions dynamically
        query = 'SELECT * FROM events WHERE 1=1'  # 1=1 ensures the query is always valid
        if start_date:
            query += ' AND date >= %s'
            params.append(start_date)
        if end_date:
            query += ' AND date <= %s'
            params.append(end_date)
        if venue:
            query += ' AND venue LIKE %s'
            params.append(f"%{venue}%")
        if organizer:
            query += ' AND organizer LIKE %s'
            params.append(f"%{organizer}%")
        
        query += ' ORDER BY date, time'

    cursor.execute(query, tuple(params))
    events = cursor.fetchall()
    return render_template('events.html', events=events)

@app.route('/blog', methods=['GET', 'POST'])
def show_blogs():
    # Default to fetching all blogs
    category_filter = None

    if request.method == 'POST':
        # Get the category from the form
        category_filter = request.form.get('category')

    if category_filter:
        # Fetch blogs with the specified category from MongoDB
        blogs = list(mongo.db.bit.find({'category': category_filter}))
    else:
        # Fetch all blogs if no category is selected
        blogs = list(mongo.db.bit.find())

    if not blogs:
        blogs = []

    return render_template('blog.html', blogs=blogs, category_filter=category_filter)

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/quiz/python')
def python_quiz():
    return render_template('python_quiz.html')

@app.route('/quiz/dbms')
def dbms_quiz():
    return render_template('dbms_quiz.html')

@app.route('/quiz/webdev')
def webdev_quiz():
    return render_template('webdev_quiz.html')

@app.route('/add')
def add():
    return render_template('addcourse.html')

@app.route('/addcourse', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        # Form fields
        title = request.form['title']
        description = request.form['description']
        instructor_id = request.form['instructor_id']

        try:
            # Handle image upload
            image = request.files['image']
            image_filename = None
            db_image_path = None

            if image and image.filename != '':
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)
                print(f"Saved Image Path: {image_path}")

                # Save relative path to the database (with leading '/assets')
                db_image_path = f"/assets/{image_filename}"
                print(f"Database Image Path: {db_image_path}")

            # Insert into the database
            cursor = mysql.connection.cursor()
            query = """
                INSERT INTO courses (title, description, instructor_id, image_path) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (title, description, instructor_id, db_image_path))
            mysql.connection.commit()
            cursor.close()

            flash('Course added successfully!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('add_course'))

    return render_template('add_course.html')


@app.route('/update')
def update():
    return render_template('updatecourse.html')

@app.route('/updatecourse', methods=['GET', 'POST'])
def update_course():
    if request.method == 'POST':
        course_id = request.form['course_id']
        title = request.form['title']
        description = request.form['description']
        
        cursor = mysql.connection.cursor()
        query = "UPDATE courses SET title = %s, description = %s WHERE id = %s"
        cursor.execute(query, (title, description, course_id))
        mysql.connection.commit()
        affected_rows = cursor.rowcount
        cursor.close()

        if affected_rows == 0:
            return redirect(url_for('message', msg="Course not found!"))
        
        flash('Course updated successfully!')
        return redirect(url_for('dashboard'))

@app.route('/delete')
def delete():
    return render_template('deletecourse.html')

@app.route('/deletecourse', methods=['GET', 'POST'])
def delete_course():
    if request.method == 'POST':
        course_id = request.form['course_id']
        
        cursor = mysql.connection.cursor()
        query = "DELETE FROM courses WHERE id = %s"
        cursor.execute(query, (course_id,))
        mysql.connection.commit()
        affected_rows = cursor.rowcount
        cursor.close()

        if affected_rows == 0:
            return redirect(url_for('message', msg="Course not found!"))
        
        flash('Course deleted successfully!')
        return redirect(url_for('dashboard'))

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        try:
            cur = mysql.connection.cursor()
            query = "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)"
            print(f"Executing query: {query} with values: {name}, {email}, {message}")
            cur.execute(query, (name, email, message))
            mysql.connection.commit()
            cur.close()
            return "Message Sent! Thank you for reaching out."
        except Exception as e:
            print(f"Error during database operation: {e}")
            return f"An error occurred: {e}"
            
@app.route('/quiz/<quiz_name>')
def quiz(quiz_name):
    if 'loggedin' in session:
        return render_template(f'{quiz_name}.html')
    return redirect(url_for('login'))

# Submit Quiz Route (API Endpoint)
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'loggedin' in session:
        data = request.json
        quiz_name = data.get('quiz_name')
        score = data.get('score')

        # Insert quiz results into the database
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (%s, %s, %s)",
            (session['id'], quiz_name, score)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({'success': True, 'message': 'Score saved successfully!'})
    return jsonify({'success': False, 'message': 'Unauthorized access'})

@app.route('/enrol')
def enrol():
    return render_template('enrol.html')

@app.route('/courses')
def courses():
    return redirect(url_for('dashboard'))

@app.route('/webdev')
def webdev():
    return render_template('webdev.html')

@app.route('/datascience')
def datascience():
    return render_template('datascience.html')
    
@app.route('/aiml')
def aiml():
    return render_template('aiml.html')

@app.route('/java')
def java():
    return render_template('java.html')
@app.route('/dbms')
def dbms():
    return render_template('dbms.html')

if __name__ == '__main__':
    app.run(debug=True)

