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
@team_blueprint.route('/buscar', methods=['GET'])
def buscarEquipo():
    nombre = request.args.get('q', '')
    
    db = Connection()
    controller = TeamController(db)
    
    resultados = controller.buscarEquipo(nombre)
    
    return jsonify(resultados)

@team_blueprint.route('/modificar/<int:idEquipo>')
def modificar_equipo(idEquipo):
    db = Connection()
    controller = TeamController(db)
    
    json_detalle = controller.cargarDatosEquipo(idEquipo)
    
    return render_template('team/modificar_equipo.html', equipo=json_detalle)

@team_blueprint.route('/modificar/eliminar/<int:idEquipo>/<int:idUnico>')
def eliminar_pokemon_action(idEquipo, idUnico):
    db = Connection()
    controller = TeamController(db)
    
    controller.eliminarPokemonDeEquipo(idUnico)
    
    return redirect(url_for('team_bp.modificar_equipo', idEquipo=idEquipo))

@team_blueprint.route('/modificar/anadir/<int:idEquipo>', methods=['POST'])
def anadir_pokemon_action(idEquipo):
    nombrePokemon = request.form.get('nombrePokemon')
    
    db = Connection()
    controller = TeamController(db)
    
    datos_pokemon = controller.obtenerDatosPokemon(nombrePokemon)
    
    if datos_pokemon:
        controller.insertarPokemonEnEquipo(idEquipo, datos_pokemon)
    else:
        flash("Pokemon no encontrado", "error")
        
    return redirect(url_for('team_bp.modificar_equipo', idEquipo=idEquipo))

@team_blueprint.route('/modificar/guardar/<int:idEquipo>', methods=['POST'])
def guardar_cambios_equipo(idEquipo):
    nuevoNombre = request.form.get('nuevoNombre')
    
    db = Connection()
    controller = TeamController(db)
    
    controller.actualizarNombreEquipo(idEquipo, nuevoNombre)
    
    return redirect(url_for('team_bp.list_teams'))

@team_blueprint.route('/modificar/seleccionar/<int:idEquipo>')
def seleccionar_pokemon_view(idEquipo):
    db = Connection()
    controller = TeamController(db)
    pokemons = controller.consultarPokedex()
    return render_template('team/seleccionar_pokemon.html', pokemons=pokemons, idEquipo=idEquipo)

@team_blueprint.route('/modificar/agregar_seleccion/<int:idEquipo>/<int:pokedexId>')
def agregar_pokemon_seleccionado(idEquipo, pokedexId):
    db = Connection()
    controller = TeamController(db)
    exito = controller.insertarPokemonDesdePokedex(idEquipo, pokedexId)
    
    if not exito:
        flash("No se pudo añadir (¿Equipo lleno?)", "error")
    return redirect(url_for('team_bp.modificar_equipo', idEquipo=idEquipo))