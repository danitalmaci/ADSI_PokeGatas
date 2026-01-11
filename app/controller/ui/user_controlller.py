from flask import Blueprint, request, redirect, render_template, flash
from app.controller.model.user_controller import UserController


def user_blueprint(db):
    bp = Blueprint('users', __name__)
    service = UserController(db)

    # (opcional) listado de usuarios para admin/pruebas
    @bp.route('/users', methods=['GET'])
    def users():
        return render_template('users.html', users=service.get_all())

    # ✅ REGISTRO (GET muestra, POST guarda)
    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')

        try:
            service.create_account(
                nickname=request.form.get('nickname', ''),
                nombre=request.form.get('nombre', ''),
                apellido1=request.form.get('apellido1', ''),
                apellido2=request.form.get('apellido2', ''),
                correo=request.form.get('correo', ''),
                contrasena=request.form.get('contrasena', ''),
                fecha_nacimiento=request.form.get('fecha_nacimiento', ''),
                descripcion=request.form.get('descripcion', ''),
                foto=None
            )

            flash("Cuenta creada correctamente. Espera la aprobación del administrador.", "success")
            return redirect('/')

        except ValueError as e:
            flash(str(e), "error")
            return redirect('/register')

    return bp
