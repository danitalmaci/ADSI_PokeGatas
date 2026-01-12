from flask import Blueprint, render_template, session, redirect, flash, url_for, request
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

    # ✅ GET: cargar pantalla actualizar
    # ✅ POST: guardar cambios
    @bp.route("/perfil/actualizar", methods=["GET", "POST"])
    def actualizar_perfil():
        nickname_sesion = session.get("nickname")
        if not nickname_sesion:
            flash("Debes iniciar sesión.", "error")
            return redirect(url_for("users.login"))

        if request.method == "GET":
            try:
                data = pokedex.get_datos_actualizar_perfil(nickname_sesion)
            except Exception as e:
                flash(f"Error cargando datos del perfil: {e}", "error")
                return redirect(url_for("perfil.perfil"))

            return render_template("actualizar_perfil.html", data=data)

        # POST -> Guardar
        try:
            nuevo_nickname = request.form.get("nuevo_nickname", "").strip()
            nombre = request.form.get("nombre", "").strip()
            apellido1 = request.form.get("apellido1", "").strip()
            apellido2 = request.form.get("apellido2", "").strip()
            correo = request.form.get("correo", "").strip()
            fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            foto = request.form.get("foto", "").strip() or None

            pokedex.actualizar_datos_perfil(
                nickname_sesion=nickname_sesion,
                nuevo_nickname=nuevo_nickname,
                nombre=nombre,
                apellido1=apellido1,
                apellido2=apellido2,
                descripcion=descripcion,
                fecha_nacimiento=fecha_nacimiento,
                correo=correo,
                foto=foto
            )

            # Si cambió el nickname, actualizamos sesión
            session["nickname"] = nuevo_nickname

            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for("perfil.perfil"))

        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("perfil.actualizar_perfil"))
        except Exception as e:
            flash(f"Error actualizando perfil: {e}", "error")
            return redirect(url_for("perfil.actualizar_perfil"))

    return bp
