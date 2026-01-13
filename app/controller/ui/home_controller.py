from flask import Blueprint, render_template, request, redirect, flash
from app.controller.pokedex import Pokedex
from app.database.connection import Connection


def home_blueprint():
    bp = Blueprint('home', __name__)
    db = Connection()
    pokedex = Pokedex(db)

    @bp.route('/')
    def index():
        JSON_Pokedex = pokedex.mostrarPokedex()
        return render_template('pokedex_inicio.html', pokemons=JSON_Pokedex)

    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')

        try:
            pokedex.crear_cuenta(
                nickname=request.form.get('nickname', ''),
                nombre=request.form.get('nombre', ''),
                apellido1=request.form.get('apellido1', ''),
                apellido2=request.form.get('apellido2', ''),
                correo=request.form.get('correo', ''),
                contrasena=request.form.get('contrasena', ''),
                fecha_nacimiento=request.form.get('fecha_nacimiento', ''),
                descripcion=request.form.get('descripcion', ''),
                foto=None  # de momento no procesamos subida real
            )

            flash("Cuenta creada correctamente. Espera la aprobación del administrador.", "success")
            return redirect('/')

        except ValueError as e:
            flash(str(e), "error")
            return redirect('/register')

    return bp
