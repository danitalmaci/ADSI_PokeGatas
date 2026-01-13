from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database.connection import Connection
from app.controller.pokedex import Pokedex
from flask import jsonify

team_blueprint = Blueprint('team_bp', __name__, url_prefix='/equipos')

@team_blueprint.route('/')
def consultar_equipos():
    user_id = session.get('user_id', 1) 
    db = Connection()
    sistema = Pokedex(db)
    teams_data = sistema.obtener_equipos_usuario(user_id)
    return render_template('team/equipos.html', teams=teams_data)
    
@team_blueprint.route('/eliminar/<int:id_equipo>')
def eliminar_equipo(id_equipo):
        db = Connection()
        sistema = Pokedex(db)
        success = sistema.eliminar_equipo(id_equipo)
        
        if success:
            flash("Equipo eliminado correctamente", "success")
        else:
            flash("Error al eliminar el equipo", "error")
        
        return redirect(url_for('team_bp.consultar_equipos'))

@team_blueprint.route('/crear', methods=['GET', 'POST'])
def crear_equipo():
    # Usamos user_id = 1 simulando el nickname
    user_id = session.get('user_id', 1)
    
    db = Connection()
    sistema = Pokedex(db)

    if request.method == 'POST':
        nombre_equipo = request.form.get('nombre_equipo')
        lista_pok = request.form.getlist('pokemons')
        
        if len(lista_pok) > 6:
            flash("Máximo 6 Pokémon por equipo", "error")
            return redirect(url_for('team_bp.crear_equipo'))

        exito = sistema.crear_equipo(user_id, nombre_equipo, lista_pok)
        
        if exito:
            return redirect(url_for('team_bp.consultar_equipos'))
        else:
            flash("Error al crear equipo", "error")
            return redirect(url_for('team_bp.crear_equipo'))

    else:
        json_pokedex = sistema.mostrarPokedex()
        return render_template('team/create_team.html', pokemons=json_pokedex)

@team_blueprint.route('/ver_equipo/<nombre_equipo>')
def ver_detalle_equipo(nombre_equipo):
    
    db = Connection()
    sistema = Pokedex(db)

    json_detalle_equipo = sistema.ver_detalle_equipo(nombre_equipo)
    
    return render_template('team/ver_equipo.html', 
                           equipo=json_detalle_equipo, 
                           nombreEquipo=nombre_equipo)

@team_blueprint.route('/buscar', methods=['GET'])
def buscar_Equipo():
    nombre = request.args.get('q', '')
    
    db = Connection()
    sistema = Pokedex(db)
    
    resultados = sistema.buscar_equipo(nombre)
    
    return jsonify(resultados)

@team_blueprint.route('/modificar/<int:id_equipo>')
def modificar_equipo(id_equipo):
    db = Connection()
    sistema = Pokedex(db)
    
    json_detalle = sistema.cargar_datos_equipo(id_equipo)
    
    return render_template('team/modificar_equipo.html', equipo=json_detalle)

@team_blueprint.route('/modificar/eliminar/<int:id_equipo>/<int:id_unico>')
def eliminar_pokemon(id_equipo, id_unico):
    db = Connection()
    sistema = Pokedex(db)
    
    cantidad_actual = sistema.contar_pokemons(id_equipo)
    if cantidad_actual <= 1:
       flash("El equipo no puede quedarse vacío. Añade otro antes de borrar este.", "error") 
    else:
        sistema.eliminar_pokemon_de_equipo(id_unico)
    
    return redirect(url_for('team_bp.modificar_equipo', id_equipo=id_equipo))

@team_blueprint.route('/modificar/guardar/<int:id_equipo>', methods=['POST'])
def guardar_cambios_equipo(id_equipo):
    nuevo_nombre = request.form.get('nuevoNombre')
    
    db = Connection()
    sistema = Pokedex(db)
    
    sistema.actualizar_nombre_equipo(id_equipo, nuevo_nombre)
    
    return redirect(url_for('team_bp.consultar_equipos'))

@team_blueprint.route('/modificar/seleccionar/<int:id_equipo>')
def seleccionar_pokemon_view(id_equipo):
    db = Connection()
    sistema = Pokedex(db)
    pokemons = sistema.mostrarPokedex()
    return render_template('team/seleccionar_pokemon.html', pokemons=pokemons, id_equipo=id_equipo)

@team_blueprint.route('/modificar/agregar_seleccion/<int:id_equipo>/<int:pokedex_id>')
def agregar_pokemon_seleccionado(id_equipo, pokedex_id):
    db = Connection()
    sistema = Pokedex(db)
    datos_pokemon = sistema.obtener_pokemon_por_id(pokedex_id)
    if datos_pokemon and isinstance(datos_pokemon, dict):
        exito = sistema.insertar_pokemon_en_equipo(id_equipo, datos_pokemon)
        if not exito:
            flash("No se pudo añadir (¿Equipo lleno?)", "error")
    else:
        flash("Error al recuperar datos del Pokémon", "error")
    return redirect(url_for('team_bp.modificar_equipo', id_equipo=id_equipo))