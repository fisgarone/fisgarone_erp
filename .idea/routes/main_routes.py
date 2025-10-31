# app/routes/main_routes.py
from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html')
