from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config['SECRET_KEY'] = '@Learning_management'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student', 'instructor', 'admin'


# Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    instructor = db.relationship('User', backref='courses')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Home page
@app.route('/')
def index():
    return render_template('index.html')


#Login if already registered
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')

#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('index'))

#to register to join the learning management system
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


#The dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        courses = Course.query.all()
    else:
        courses = current_user.courses

    return render_template('dashboard.html', courses=courses, user=current_user)


@app.route('/course/<int:course_id>')
@login_required
def course(course_id):
    course = Course.query.get(course_id)
    return render_template('course.html', course=course)

#function to create course
@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        new_course = Course(title=title, description=description, instructor=current_user)
        db.session.add(new_course)
        db.session.commit()

        flash('Course created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_course.html')

#To run it
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)
