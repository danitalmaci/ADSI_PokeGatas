from flask import Blueprint, render_template, request, redirect, flash
from app.controller.model.user_controller import UserController
from app.database.connection import Connection


def home_blueprint():
    bp = Blueprint('home', __name__)
    db = Connection()
    user_service = UserController(db)

    @bp.route('/')
    def index():
        return render_template('login.html')

    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        # GET → mostrar formulario
        if request.method == 'GET':
            return render_template('register.html')

        # POST → procesar registro (caso de uso Registrarse)
        try:
            user_service.create_account(
                nickname=request.form['nickname'],
                nombre=request.form['nombre'],
                apellido1=request.form['apellido1'],
                apellido2=request.form['apellido2'],
                foto=None,  # de momento no procesamos subida real
                contrasena=request.form['contrasena'],
                correo=request.form['correo'],
                fecha_nacimiento=request.form['fecha_nacimiento'],
                descripcion=request.form['descripcion']
            )

            flash("Cuenta creada correctamente. Espera la aprobación del administrador.", "success")
            return redirect('/')

        except ValueError as e:
            flash(str(e), "error")
            return redirect('/register')

    return bp
