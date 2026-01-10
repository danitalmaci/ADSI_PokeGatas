from flask import Blueprint, render_template, redirect
def pokedex_blueprint():
    bp = Blueprint('pokedex', __name__)

    @bp.route('/pokedex', methods=['GET', 'POST'])
    def pokedex():
        return render_template('pokedex.html')

    return bp