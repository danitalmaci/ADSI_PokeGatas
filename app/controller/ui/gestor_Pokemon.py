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
        JSON_Pokemon = pokedex.mostrarPokemon(nombrePokemon) 
        if JSON_Pokemon: 
            pokemon_data = JSON_Pokemon[0] 
        else: 
            pokemon_data = {} 
        return render_template('pokemon.html', pokemon=pokemon_data) 
    
    return bp
