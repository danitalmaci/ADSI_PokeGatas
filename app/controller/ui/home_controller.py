from flask import Blueprint, render_template, redirect

def home_blueprint():
    bp = Blueprint('home', __name__)

    @bp.route('/')
    def index():
        return render_template('login.html')

    return bp