from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.connection import Connection
from app.controller.model.team_controller import TeamController
from flask import jsonify

team_blueprint = Blueprint('team_bp', __name__, url_prefix='/equipos')

@team_blueprint.route('/')
def list_teams():
    user_id = session.get('user_id', 1) 
    
    db = Connection()
    controller = TeamController(db) 
    teams_data = controller.get_teams_by_user(user_id)
    
    return render_template('team/equipos.html', teams=teams_data)
    
@team_blueprint.route('/eliminar/<int:team_id>')
def delete_team(team_id):
        db = Connection()
        controller = TeamController(db)
        success = controller.delete_team(team_id)
        
        if success:
            flash("Equipo eliminado correctamente", "success")
        else:
            flash("Error al eliminar el equipo", "error")
        
        return redirect(url_for('team_bp.list_teams'))

@team_blueprint.route('/crear', methods=['GET', 'POST'])
def create_team():
    # Usamos user_id = 1 simulando el nickname
    nickname = 1 
    
    db = Connection()
    controller = TeamController(db)

    if request.method == 'POST':
        nombreEquipo = request.form.get('nombre_equipo')
        lista_pok = request.form.getlist('pokemons')
        
        if len(lista_pok) > 6:
            flash("Máximo 6 Pokémon por equipo", "error")
            return redirect(url_for('team_bp.create_team'))

        exito = controller.crearEquipo(nickname, nombreEquipo, lista_pok)
        
        if exito:
            return redirect(url_for('team_bp.list_teams'))
        else:
            flash("Error al crear equipo", "error")
            return redirect(url_for('team_bp.create_team'))

    else:
        json_pokedex = controller.consultarPokedex()
        return render_template('team/create_team.html', pokemons=json_pokedex)

@team_blueprint.route('/ver_equipo/<nombreEquipo>')
def consultarDetalleEquipo(nombreEquipo):
    
    db = Connection()
    controller = TeamController(db)

    json_detalle_equipo = controller.verDetalleEquipo(nombreEquipo)
    
    return render_template('team/ver_equipo.html', 
                           equipo=json_detalle_equipo, 
                           nombreEquipo=nombreEquipo)