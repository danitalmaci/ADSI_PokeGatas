from flask import Blueprint, request, redirect, render_template, flash, session, url_for
from app.controller.model.user_controller import UserController


def user_blueprint(db):
    bp = Blueprint('users', __name__)
    service = UserController(db)

    # (opcional) listado de usuarios para admin/pruebas
    @bp.route('/users', methods=['GET'])
    def users():
        return render_template('users.html', users=service.get_all())

    # ✅ LOGIN (GET muestra, POST comprueba)
    @bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')

        nickname = request.form.get('nickname', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        ok = service.iniciarSesion(nickname, contrasena)

        if ok == 1:
            # Guardar quién ha iniciado sesión
            session['nickname'] = nickname

            flash("Sesión iniciada correctamente.", "success")

            # Redirigir al menú (ajusta esta ruta a la tuya si no es /menu)
            return redirect('/menu_logged')

        flash("Nickname o contraseña incorrectos.", "error")
        return redirect(url_for('users.login'))

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
