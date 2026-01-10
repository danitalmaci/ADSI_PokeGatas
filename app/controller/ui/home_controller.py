from flask import Blueprint, render_template, redirect

# Aquí se define el blueprint para las rutas de la página de inicio y el dashboard, es el archivo que gestiona a que html se redirige cada botón.

def home_blueprint():
    bp = Blueprint('home', __name__)


    @bp.route('/')
    def index():
        return render_template('login.html')


    @bp.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        return render_template('dashboard.html') 

    return bp