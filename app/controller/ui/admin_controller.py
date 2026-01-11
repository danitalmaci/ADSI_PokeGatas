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
        # 1. Recogemos el parámetro 'search' de la URL (si existe)
        search_query = request.args.get('search')
        
        # 2. Llamamos a la lógica de negocio pasando el filtro
        # Si search_query es None, el modelo devolverá todos (como antes)
        users = admin_service.get_active_users(filtro_nombre=search_query)
        
        # 3. Renderizamos la vista pasando los datos
        return render_template('admin/dashboard.html', users=users)
    @bp.route('/pendientes', methods=['GET'])
    def pending_users():
        # users = admin_service.get_pending_users()
        return "<h1>TO DO: Pagina de usuarios pendientes</h1>"

    return bp