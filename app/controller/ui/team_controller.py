from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.connection import Connection
# Importamos el modelo que acabamos de crear
from app.controller.model.team_controller import TeamController

# Definimos el Blueprint con prefijo '/equipos'
team_blueprint = Blueprint('team_bp', __name__, url_prefix='/equipos')

# RUTA 1: Listar Equipos (Necesario para ver el botón de borrar)
@team_blueprint.route('/')
def list_teams():
    # OJO: Aquí deberíamos coger el ID del usuario logueado.
    # Como aún no tenemos el Login 100% integrado, usamos 1 por defecto para probar.
    user_id = session.get('user_id', 1) 
    
    db = Connection()
    controller = TeamController(db)
    
    # Llamamos al método del modelo
    teams_data = controller.get_teams_by_user(user_id)
    
    return render_template('equipos.html', teams=teams_data)

# RUTA 2: Eliminar Equipo (Implementación del Diagrama 9.23)
@team_blueprint.route('/eliminar/<int:team_id>')
def delete_team(team_id):
    db = Connection()
    controller = TeamController(db)
    
    # 1. Llamamos al método delete_team del Modelo (Paso 4 del diagrama)
    success = controller.delete_team(team_id)
    
    # 2. Feedback visual (Paso 6 del diagrama: "mostrarMensaje")
    if success:
        flash("Equipo eliminado correctamente", "success")
    else:
        flash("Error al eliminar el equipo", "error")
    
    # 3. Recargamos la lista (Paso 5 del diagrama: "eliminarEquipoDeLista" -> recargar página)
    return redirect(url_for('team_bp.list_teams'))