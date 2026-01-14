from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.controller.pokedex import Pokedex


def pokedex_blueprint(db):
    bp = Blueprint('pokedex', __name__)
    pokedex = Pokedex(db)

    @bp.route('/pokedex', methods=['GET'])
    def mostrarPokedex():
        nickname = session.get("nickname")  # puede ser None si no hay login
        JSON_Pokedex = pokedex.mostrarPokedex(nickname)
        return render_template('pokedex.html', pokemons=JSON_Pokedex)

    @bp.route('/pokedex/<nombrePokemon>', methods=['GET'])
    def mostrarPokemon(nombrePokemon):
        pokemon_data = pokedex.mostrarPokemon(nombrePokemon)
        if not pokemon_data:
            pokemon_data = {}
        return render_template('pokemon.html', pokemon=pokemon_data)

    # ⭐ Toggle favorito (POST)
    @bp.route('/pokedex/<nombrePokemon>/favorito', methods=['POST'])
    def anadir_favorito(nombrePokemon):
        nickname = session.get("nickname")
        if not nickname:
            flash("Debes iniciar sesión para añadir favoritos.", "error")
            return redirect(url_for("users.login"))

        nombrePokemon = (nombrePokemon or "").strip()
        if not nombrePokemon:
            flash("Pokémon inválido.", "error")
            return redirect(url_for("pokedex.mostrarPokedex"))

        # ✅ Recuperar filtros desde el form (hidden inputs)
        filtro_nombre = (request.form.get("nombre") or "").strip()
        filtro_tipo = (request.form.get("tipo") or "").strip()

        try:
            accion = pokedex.toggle_favorito(nickname, nombrePokemon)  # "anadido" | "quitado"

            if accion == "anadido":
                flash(f"★ {nombrePokemon} añadido a favoritos.", "success")

                # ✅ NOTIFICACIÓN (solo al añadir)
                pokedex.crear_notificacion(
                    nickname,
                    f"⭐ ¡Nuevo favorito! Has añadido a {nombrePokemon} a tus favoritos."
                )
            else:
                flash(f"☆ {nombrePokemon} eliminado de favoritos.", "success")

        except Exception as e:
            flash(f"Error gestionando favorito: {e}", "error")

        # ✅ Volver a pokedex manteniendo filtros si existían
        params = {}
        if filtro_nombre:
            params["nombre"] = filtro_nombre
        if filtro_tipo:
            params["tipo"] = filtro_tipo

        return redirect(url_for("pokedex.mostrarPokedex", **params))

    return bp
