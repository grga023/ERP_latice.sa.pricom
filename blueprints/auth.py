"""
Auth Blueprint - Autentifikacija korisnika
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def landing():
    """Landing page - prikazuje se ako korisnik nije ulogovan"""
    if current_user.is_authenticated:
        return redirect(url_for('orders.index'))
    return render_template('landing.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login stranica"""
    if current_user.is_authenticated:
        return redirect(url_for('orders.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('orders.index'))
        else:
            flash('Pogrešno korisničko ime ili lozinka!', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout korisnika"""
    logout_user()
    return redirect(url_for('auth.landing'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registracija novog korisnika"""
    if current_user.is_authenticated:
        return redirect(url_for('orders.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validacija
        if not username or not email or not password:
            flash('Sva polja su obavezna!', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Lozinke se ne podudaraju!', 'error')
            return render_template('register.html')
        
        # Provera da li korisnik već postoji
        if User.query.filter_by(username=username).first():
            flash('Korisničko ime već postoji!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email već postoji!', 'error')
            return render_template('register.html')
        
        # Kreiraj novog korisnika
        user = User(
            username=username,
            email=email,
            created_at=datetime.now().isoformat()
        )
        user.set_password(password)
        
        # Prvi korisnik je automatski admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registracija uspešna! Možete se ulogovati.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/api/user/profile')
@login_required
def user_profile():
    """API endpoint za user profile"""
    return jsonify(current_user.to_dict())
