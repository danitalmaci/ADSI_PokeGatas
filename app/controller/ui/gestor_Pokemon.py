from flask import Blueprint, render_template, redirect
from app.controller.model.gestor_Pokemon import gestorPokemon
from app.database.connection import Connection
from flask import jsonify


def pokedex_blueprint():
    bp = Blueprint('pokedex', __name__)

    @bp.route('/pokedex', methods=['GET', 'POST'])
    def mostrarPokedex():
        db = Connection()
        controller = gestorPokemon(db)
        JSON_Pokedex = controller.mostrarPokedex()
        return render_template('pokedex.html', pokemons=JSON_Pokedex)

    @bp.route('/pokedex/<nombrePokemon>')
    def mostrarPokemon(nombrePokemon):
        db = Connection()
        controller = gestorPokemon(db)
        JSON_Pokemon = controller.mostrarPokedex()
        return render_template('pokemon.html',pokemon=JSON_Pokemon)

    return bp