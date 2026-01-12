from flask import Blueprint, render_template, session, redirect, flash
from app.controller.pokedex import Pokedex


def perfil_blueprint(db):
    bp = Blueprint("perfil", __name__)
    pokedex = Pokedex(db)

    @bp.route("/perfil", methods=["GET"])
    def perfil():
        nickname = session.get("nickname")

        # TEMPORAL (para pruebas si aún no hay login real)
        if not nickname:
            nickname = "junec"
            session["nickname"] = nickname
            flash("⚠️ No había sesión, usando nickname de prueba", "error")

        try:
            data = pokedex.consultar_perfil(nickname)
        except Exception as e:
            flash(f"Error consultando perfil: {e}", "error")
            return redirect("/")

        return render_template("perfil.html", data=data)

    return bp
