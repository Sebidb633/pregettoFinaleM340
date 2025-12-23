from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from models.connection import db
from models.model import User

app = Blueprint('auth', __name__)

@app.route('/')
def login():
    if current_user.is_authenticated:
        flash('User already authenticated.')
        return redirect(url_for('default.request_vm'))
    else:
        return render_template('/auth/login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    stmt = db.select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user:
        if user.check_password(password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('default.request_vm'))
        else:
            flash('Invalid password. Please try again.')
            return redirect(url_for('auth.login'))
    else:
        flash('Invalid account. Please try again.')
        return redirect(url_for('auth.login'))


@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    return render_template('/auth/logout.html', name=username)
