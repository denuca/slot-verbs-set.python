from flask import Blueprint, render_template

view_bp = Blueprint("view_bp", __name__)

@view_bp.route("/")
def home():
    """Render the slot machine frontend"""
    return render_template("index.html")
