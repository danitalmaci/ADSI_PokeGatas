from flask import Blueprint, render_template, session, redirect, flash
from app.controller.model.user_controller import UserController


def perfil_blueprint(db):
    bp = Blueprint("perfil", __name__)
    user_service = UserController(db)

    @bp.route("/perfil", methods=["GET"])
    def perfil():
        # 1) Sacar nickname desde sesión
        nickname = session.get("nickname")

        # 🔧 TEMPORAL (para pruebas si aún no hay login real)
        # Si no hay nickname en sesión, ponemos uno de prueba (cámbialo por uno que exista en tu BD)
        if not nickname:
            nickname = "junec"
            session["nickname"] = nickname
            flash("⚠️ No había sesión, usando nickname de prueba", "error")

        # 2) Llamar a la lógica (MVC) como en la documentación
        try:
            data = user_service.consultar_perfil(nickname)
        except Exception as e:
            flash(f"Error consultando perfil: {e}", "error")
            return redirect("/")

        # 3) Renderizar vista
        return render_template("perfil.html", data=data)

    return bp
