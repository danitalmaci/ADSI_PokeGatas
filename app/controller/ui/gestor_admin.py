# app/controller/ui/admin_controller.py
from flask import Blueprint, render_template, request, redirect, url_for
from app.controller.pokedex import Pokedex

def admin_blueprint(db):
    bp = Blueprint('admin', __name__, url_prefix='/admin')
    
    pokedex = Pokedex(db)

    @bp.route('/users', methods=['GET'])
    def admin_users():
        search_query = request.args.get('search')
        users = pokedex.obtenerCuentas(filtro_nombre=search_query)
        return render_template('admin/dashboard.html', users=users)
    
    @bp.route('/pendientes', methods=['GET'])
    def pending_users():
        users = pokedex.obtenerCuentasPendientes()
        return render_template('admin/pending_users.html', users=users)

    @bp.route('/approve/<string:nickname>', methods=['GET'])
    def approve_user(nickname):
        pokedex.aprobarCuenta(nickname)
        return redirect(url_for('admin.pending_users'))

    @bp.route('/delete/<string:nickname>', methods=['GET'])
    def delete_user(nickname):
        pokedex.borrarCuenta(nickname)
        return redirect(request.referrer or url_for('admin.admin_users'))
    
    @bp.route('/edit/<string:nickname>', methods=['GET'])
    def edit_user_form(nickname):
        user = pokedex.get_datos_actualizar_perfil(nickname)
        if not user:
            return "Usuario no encontrado", 404
        return render_template('admin/edit_user.html', user=user)

    @bp.route('/update', methods=['POST'])
    def update_user():
        pokedex.modificarCuenta(
            antiguo_nick=request.form['antiguo_nickname'],
            nuevo_nick=request.form['nickname'],
            nombre=request.form['nombre'],
            ape1=request.form['ape1'],
            ape2=request.form['ape2'],
            desc=request.form['descripcion']
        )
        return redirect(url_for('admin.admin_users'))

    return bp