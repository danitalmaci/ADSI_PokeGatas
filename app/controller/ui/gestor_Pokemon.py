from flask import Blueprint, render_template, redirect
from app.controller.pokedex import Pokedex
from app.database.connection import Connection
from flask import jsonify


def pokedex_blueprint(db):
    bp = Blueprint('pokedex', __name__)
    pokedex = Pokedex(db)

    @bp.route('/pokedex', methods=['GET', 'POST'])
    def mostrarPokedex():
        JSON_Pokedex = pokedex.mostrarPokedex()
        return render_template('pokedex.html', pokemons=JSON_Pokedex)

    @bp.route('/pokedex/<nombrePokemon>') 
    def mostrarPokemon(nombrePokemon):
        # Obtener el JSON del Pokémon
        pokemon_data = pokedex.mostrarPokemon(nombrePokemon)  # ya es dict
        if not pokemon_data:
            # Si no existe el Pokémon, puedes redirigir, mostrar error o un dict vacío
            pokemon_data = {}

        # Renderizar el template con el dict
        return render_template('pokemon.html', pokemon=pokemon_data)
    
    return bp
