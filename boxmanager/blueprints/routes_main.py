from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from ..models import User, Box, Item
from .. import db, login_manager

# Blueprint setup
main = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(uuid.UUID(user_id))
    except ValueError:
        return None


@main.route('/')
def home():
    if current_user.is_authenticated:
        return f'Hello, {current_user.username}! <a href="/logout">Logout</a>'
    else:
        return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('main.register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))
    return render_template('register.html')  # pragma: no cover


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
