# app.py
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Book
from forms import RegistrationForm, LoginForm, BookForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
# app.py (continued)
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # In a real application, use hashed passwords!
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(title=form.title.data, author=form.author.data, genre=form.genre.data, available_copies=form.available_copies.data)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    
    all_books = Book.query.all()
    return render_template('books.html', form=form, books=all_books)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)