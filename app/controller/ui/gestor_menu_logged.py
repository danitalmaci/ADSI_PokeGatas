from flask import Blueprint, render_template, session, redirect, url_for
from app.controller.pokedex import Pokedex


def menu_logged_blueprint(db):
    bp = Blueprint('menu_logged', __name__)
    pokedex = Pokedex(db)

    @bp.route('/menu_logged', methods=['GET'])
    def menu_logged():
        # Protección: solo usuarios logueados
        if "nickname" not in session:
            return redirect(url_for('users.login'))

        # 🔹 Reutilizamos la lógica existente de la Pokédex
        pokemons = pokedex.mostrarPokedex()

        return render_template(
            'menu_logged.html',
            pokemons=pokemons
        )

    return bp
