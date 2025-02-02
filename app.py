# Comprehensive Educational Website using Flask

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from markdown2 import markdown
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education_site.db'  # Use MySQL in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
mail = Mail(app)

# Database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    audio_url = db.Column(db.String(200))
    video_url = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)  # E.g., "Tajweed", "Arabic", "Islamic Studies"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question = db.Column(db.String(200), nullable=False)
    options = db.Column(db.String(500), nullable=False)  # Comma-separated options
    correct_option = db.Column(db.String(100), nullable=False)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    lessons = Lesson.query.all()
    return render_template('index.html', lessons=lessons)
@app.route('/index')
def index():
    lessons = Lesson.query.all()
    return render_template('index.html', lessons=lessons)
@app.route('/tajweed')
def tajweed():
    lessons = Lesson.query.all()
    return render_template('tajweed.html', lessons=lessons)
@app.route('/islamic')
def islamic():
    lessons = Lesson.query.all()
    return render_template('islamic.html', lessons=lessons)
@app.route('/arabic')
def arabic():
    lessons = Lesson.query.all()
    return render_template('arabic.html', lessons=lessons)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        # تحقق من تطابق كلمة المرور مع تأكيد كلمة المرور
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة، يرجى المحاولة مرة أخرى.', 'danger')
            return redirect(url_for('register'))

        # إنشاء مستخدم جديد وإضافته إلى قاعدة البيانات
        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('تم إنشاء الحساب بنجاح!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/lessons/<category>')
def lessons_by_category(category):
    lessons = Lesson.query.filter_by(category=category).all()
    return render_template('lessons.html', category=category, lessons=lessons)

@app.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('lesson_detail.html', lesson=lesson)

@app.route('/quiz/<int:lesson_id>', methods=['GET', 'POST'])
def quiz(lesson_id):
    if request.method == 'POST':
        score = 0
        questions = Quiz.query.filter_by(lesson_id=lesson_id).all()
        for question in questions:
            user_answer = request.form.get(str(question.id))
            if user_answer == question.correct_option:
                score += 1
        flash(f'Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('lesson_detail', lesson_id=lesson_id))

    questions = Quiz.query.filter_by(lesson_id=lesson_id).all()
    return render_template('quiz.html', questions=questions)



# بيانات افتراضية للفصول والأقسام
chapters = [
    {
        "id": 1,
        "name": "الفصل الأول",
        "children": [
            {"id": 101, "name": "مقدمة", "content": "هذا هو شرح مقدمة الفصل الأول."},
            {"id": 102, "name": "موضوع 1", "content": "هذا هو شرح موضوع 1 في الفصل الأول."},
        ],
    },
    {
        "id": 2,
        "name": "الفصل الثاني",
        "children": [
            {"id": 201, "name": "مقدمة", "content": "هذا هو شرح مقدمة الفصل الثاني."},
            {"id": 202, "name": "موضوع 1", "content": "هذا هو شرح موضوع 1 في الفصل الثاني."},
        ],
    },
]

@app.route("/chapter-view")
def chapter_view():
    return render_template("chapter_view.html", chapters=chapters, selected_section=None)

@app.route("/section/<int:section_id>")
def view_section(section_id):
    # البحث عن القسم المطلوب
    selected_section = None
    for chapter in chapters:
        for child in chapter["children"]:
            if child["id"] == section_id:
                selected_section = child
                break
    return render_template("chapter_view.html", chapters=chapters, selected_section=selected_section)
@app.route("/letters")
def letters():
    return render_template("letters.html")
# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
