from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

from . import auth_bp
from models import db, User

# WTForms for Login & Signup
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])

# Authentication Routes

@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('converter.dashboard'))
    return render_template('home.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('converter.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email_val = form.email.data.strip()
        if "@" not in email_val or "." not in email_val:
            form.email.errors.append("Invalid email address format.")
            return render_template('login.html', form=form)
            
        user = User.query.filter_by(email=email_val).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}! Secure connection established.", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('converter.dashboard'))
        else:
            flash("Invalid authorization credentials. Please verify your email and pass-key.", "danger")
            
    return render_template('login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('converter.dashboard'))
        
    form = SignupForm()
    if form.validate_on_submit():
        email_val = form.email.data.strip()
        if "@" not in email_val or "." not in email_val:
            form.email.errors.append("Invalid email address format.")
            return render_template('signup.html', form=form)
            
        # Check if username or email already registered
        existing_username = User.query.filter_by(username=form.username.data.strip()).first()
        existing_email = User.query.filter_by(email=email_val).first()
        
        if existing_username:
            form.username.errors.append("Username is already linked to an identity.")
        elif existing_email:
            form.email.errors.append("Email is already linked to an identity.")
        else:
            # Create user and encrypt password hash
            hashed_pwd = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(
                username=form.username.data.strip(),
                email=email_val,
                password_hash=hashed_pwd
            )
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            flash("Identity successfully initialized. Welcome to the Converter Pro grid!", "success")
            return redirect(url_for('converter.dashboard'))
            
    return render_template('signup.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Session terminated successfully. Secure locks engaged.", "success")
    return redirect(url_for('auth.home'))
