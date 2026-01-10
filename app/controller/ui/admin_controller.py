# app/controller/ui/admin_controller.py
from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.controller.model.admin_controller import AdminController

def admin_blueprint(db):
    # Blueprint con prefijo /admin
    bp = Blueprint('admin', __name__, url_prefix='/admin')

    # Instanciamos el servicio del modelo pasándole la base de datos
    admin_service = AdminController(db)

    @bp.route('/users', methods=['GET'])
    def admin_users():
        # 1. Llamamos a la lógica de negocio
        users = admin_service.get_active_users()
        
        # 2. Renderizamos la vista pasando los datos
        return render_template('admin/dashboard.html', users=users)
    
    @bp.route('/delete/<string:nickname>', methods=['GET'])
    def delete_user(nickname):
        # llamada al modelo para borrar la cuenta
        admin_service.borrarCuenta(nickname)
        # volver a la vista de admin users
        return redirect(url_for('admin.admin_users'))
    
    # formulario para editar usuario
    @bp.route('/edit/<string:nickname>', methods=['GET'])
    def edit_user_form(nickname):
        # buscar usuario
        user = admin_service.get_user_by_nickname(nickname)
        if not user:
            return "Usuario no encontrado", 404
        return render_template('admin/edit_user.html', user=user)

    # boton guardar cambios del formulario
    @bp.route('/update', methods=['POST'])
    def update_user():       
        # recoger datos
        antiguo_nick = request.form['antiguo_nickname']
        nuevo_nick = request.form['nickname']
        nombre = request.form['nombre']
        ape1 = request.form['ape1']
        ape2 = request.form['ape2']
        desc = request.form['descripcion']
        
        # llamada al modelo
        admin_service.update_user(antiguo_nick, nuevo_nick, nombre, ape1, ape2, desc)
        
        # volver al dashboard
        return redirect(url_for('admin.admin_users'))
    
    # Vista de lista de pendientes
    @bp.route('/pendientes', methods=['GET'])
    def pending_users():
        users = admin_service.get_pending_users()
        return render_template('admin/pending_users.html', users=users)

    # Aprobar cuenta
    @bp.route('/approve/<string:nickname>', methods=['GET'])
    def approve_user(nickname):
        # llamar al modelo
        admin_service.aprobarCuenta(nickname)
        # recargar pagina
        return redirect(url_for('admin.pending_users'))

    return bp