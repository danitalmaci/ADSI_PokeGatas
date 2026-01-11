from werkzeug.security import generate_password_hash
from app.database.connection import Connection


def anadir_usuarios():
    print("Iniciando carga de USUARIOS de prueba...")

    db = Connection()

    # Aseguramos que la tabla exista
    try:
        db.init_schema()
        # Limpiamos usuarios anteriores para no duplicar errores de UNIQUE
        db.delete("DELETE FROM Usuario")
        # Reiniciamos el contador del ID autoincremental (opcional, para limpieza)
        db.delete("DELETE FROM sqlite_sequence WHERE name='Usuario'")
        print("Tabla Usuario limpiada.")
    except Exception as e:
        print(f"Nota: {e}")

    # --- DATOS DE PRUEBA ---
    usuarios_fake = [
        {
            "user": "admin_jefe",
            "nombre": "David",
            "ape1": "Team",
            "ape2": "Rocket",
            "desc": "Administrador supremo del sistema.",
            "pass": "admin123",
            "mail": "boss@rocket.com",
            "nac": "2005-09-01",
            "rol": 2,  # Administrador
            "foto": "static/img/users/admin.jpg"
        },
        {
            "user": "ash_ketchum",
            "nombre": "Ash",
            "ape1": "Ketchum",
            "ape2": "Pueblo Paleta",
            "desc": "Quiero ser el mejor, mejor que nadie más.",
            "pass": "pikachu",
            "mail": "ash@pokemon.com",
            "nac": "1997-04-01",
            "rol": 1,  # Entrenador aprobado
            "foto": "static/img/users/ash.jpg"
        },
        {
            "user": "gary_oak",
            "nombre": "Gary",
            "ape1": "Oak",
            "ape2": "Profesor",
            "desc": "¡Ash es un perdedor!",
            "pass": "gary123",
            "mail": "gary@oaklab.com",
            "nac": "1997-05-01",
            "rol": 0,  # Pendiente
            "foto": "static/img/users/gary.jpg"
        },
        {
            "user": "jessie_rocket",
            "nombre": "Jessie",
            "ape1": "Musashi",
            "ape2": "Rocket",
            "desc": "Prepárense para los problemas.",
            "pass": "wobbuffet",
            "mail": "jessie@rocket.com",
            "nac": "1995-10-12",
            "rol": 0,  # Pendiente
            "foto": "static/img/users/jessie.jpg"
        }
    ]

    count = 0

    # ✅ IMPORTANTE: usamos "contrasena" (sin ñ) para que coincida con schema.sql
    query = """
        INSERT INTO Usuario (
            nombreUsuario, nombre, apellido1, apellido2,
            foto, descripcion, contrasena, correo, fechaNacimiento,
            rol
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for u in usuarios_fake:
        try:
            password_encriptada = generate_password_hash(u["pass"])

            params = (
                u["user"],
                u["nombre"],
                u["ape1"],
                u["ape2"],
                u["foto"],
                u["desc"],
                password_encriptada,
                u["mail"],
                u["nac"],
                u["rol"]
            )

            db.insert(query, params)
            count += 1
            print(f"Usuario creado: {u['user']} (rol={u['rol']})")

        except Exception as e:
            print(f"Error creando {u['user']}: {e}")

    print(f"\nCarga de usuarios finalizada. Total: {count}")


if __name__ == "__main__":
    anadir_usuarios()
