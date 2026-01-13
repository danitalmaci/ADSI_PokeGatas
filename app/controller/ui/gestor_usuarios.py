from flask import Blueprint, request, redirect, render_template, flash, session, url_for
from app.controller.pokedex import Pokedex

def user_blueprint(db):
    bp = Blueprint('users', __name__)
    pokedex = Pokedex(db)

    @bp.route('/users', methods=['GET'])
    def users():
        return render_template('users.html', users=pokedex.listar_usuarios())

    @bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')

        nickname = request.form.get('nickname', '').strip()
        contrasena = request.form.get('contrasena', '').strip()

        ok = pokedex.iniciar_sesion(nickname, contrasena)

        if ok == 1:
            session['nickname'] = nickname
            flash("Sesión iniciada correctamente.", "success")
            return redirect('pokedex')

        flash("Nickname o contraseña incorrectos.", "error")
        return redirect(url_for('users.login'))

    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')

        try:
            foto = request.form.get('foto', '').strip() or None

            pokedex.crear_cuenta(
                nickname=request.form.get('nickname', ''),
                nombre=request.form.get('nombre', ''),
                apellido1=request.form.get('apellido1', ''),
                apellido2=request.form.get('apellido2', ''),
                correo=request.form.get('correo', ''),
                contrasena=request.form.get('contrasena', ''),
                fecha_nacimiento=request.form.get('fecha_nacimiento', ''),
                descripcion=request.form.get('descripcion', ''),
                foto=foto
            )

            flash("Cuenta creada correctamente. Espera la aprobación del administrador.", "success")
            return redirect('/')

        except ValueError as e:
            flash(str(e), "error")
            return redirect('/register')
    
    @bp.route('/notificaciones', methods=['GET', 'POST'])
    def mostrarNotificaciones():
        nickname = session.get("nickname")

        JSON_Notificaciones = pokedex.mostrarNotificaciones(nickname)
        return render_template('notificaciones.html', notificaciones=JSON_Notificaciones)

    return bp
