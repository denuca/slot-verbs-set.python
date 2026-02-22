from flask import Blueprint, render_template
from datetime import datetime

view_bp = Blueprint("view_bp", __name__)

@view_bp.route("/")
def home():
    """Render the slot machine frontend"""
    # Get current year
    current_year = datetime.now().year
    return render_template("index.html", current_year=current_year)

@view_bp.route("/credits")
def credits():
    """Render the credit page"""
    return render_template("credits.html")