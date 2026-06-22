from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('web.index'))
        flash('Identifiants incorrects', 'error')
    return render_template('login.html')

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password required', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('register.html')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('web.index'))
    return render_template('register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.index'))
