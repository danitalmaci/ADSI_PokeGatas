from werkzeug.security import generate_password_hash
from app.database.connection import Connection


def anadir_usuarios():
    print("Iniciando carga de USUARIOS de prueba...")

    db = Connection()

    # Aseguramos que la tabla exista
    try:
        db.init_schema()

        # Limpiamos tablas para no duplicar (orden: relaciones primero)
        db.delete("DELETE FROM PokemonFavoritos")
        db.delete("DELETE FROM Sigue")
        db.delete("DELETE FROM Usuario")

        # Nota: Usuario NO es AUTOINCREMENT (es TEXT PK), así que sqlite_sequence no aplica.
        # Si te da error esta línea, bórrala sin problema.
        try:
            db.delete("DELETE FROM sqlite_sequence WHERE name='Usuario'")
        except Exception:
            pass

        print("Tablas Usuario, Sigue y PokemonFavoritos limpiadas.")
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
            "rol": 2,
            "foto": "static/img/usuario/user4.png"
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
            "rol": 1,
            "foto": "static/img/usuario/user3.png"
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
            "rol": 0,
            "foto": "static/img/usuario/user10.png"
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
            "rol": 0,
            "foto": "static/img/usuario/user5.png"
        }
    ]

    # ---------- INSERT USUARIOS ----------
    query_usuario = """
        INSERT INTO Usuario (
            nombreUsuario, nombre, apellido1, apellido2,
            foto, descripcion, contrasena, correo, fechaNacimiento,
            rol
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for u in usuarios_fake:
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

        db.insert(query_usuario, params)
        print(f"Usuario creado: {u['user']}")

    # ---------- INSERT SIGUE ----------
    print("\nIniciando carga de relaciones SIGUE...")

    sigue_fake = [
        ("gary_oak", "ash_ketchum"),        # Ash sigue a Gary
        ("jessie_rocket", "ash_ketchum"),   # Ash sigue a Jessie
        ("ash_ketchum", "gary_oak"),        # Gary sigue a Ash
        ("ash_ketchum", "admin_jefe"),      # Admin sigue a Ash
        ("gary_oak", "admin_jefe"),         # Admin sigue a Gary
        ("jessie_rocket", "admin_jefe"),    # Admin sigue a Jessie
    ]

    query_sigue = """
        INSERT INTO Sigue (nombreUsuarioSeguido, nombreUsuarioSeguidor)
        VALUES (?, ?)
    """

    for seguido, seguidor in sigue_fake:
        try:
            db.insert(query_sigue, (seguido, seguidor))
            print(f"{seguidor} sigue a {seguido}")
        except Exception as e:
            print(f"Error en relación {seguidor} -> {seguido}: {e}")

    # ---------- INSERT FAVORITOS ----------
    print("\nIniciando carga de POKEMON FAVORITOS...")

    # OJO: estos nombres deben existir en PokemonPokedex(nombrePokemon)
    # En tu seed: nombre = data['name'].capitalize() -> Ej: "Pikachu", "Bulbasaur"
    favoritos_fake = [
        ("ash_ketchum", "Pikachu"),
        ("ash_ketchum", "Bulbasaur"),
        ("ash_ketchum", "Charizard"),

        ("gary_oak", "Eevee"),
        ("gary_oak", "Blastoise"),

        ("jessie_rocket", "Meowth"),
        ("jessie_rocket", "Wobbuffet"),

        ("admin_jefe", "Mew"),
        ("admin_jefe", "Mewtwo"),
    ]

    query_fav = """
        INSERT OR IGNORE INTO PokemonFavoritos (nombreUsuario, nombrePokemon)
        VALUES (?, ?)
    """

    for nick, nombre_poke in favoritos_fake:
        try:
            # (Opcional) Comprobación rápida de que existe el Pokémon en la Pokedex
            existe = db.select(
                sentence="SELECT 1 FROM PokemonPokedex WHERE nombrePokemon = ? LIMIT 1",
                parameters=[nombre_poke]
            )
            if not existe:
                print(f"⚠️ No existe en PokemonPokedex: {nombre_poke} (no se inserta favorito para {nick})")
                continue

            db.insert(query_fav, (nick, nombre_poke))
            print(f"Favorito insertado: {nick} -> {nombre_poke}")
        except Exception as e:
            print(f"Error insertando favorito {nick} -> {nombre_poke}: {e}")

    print("\nCarga de datos finalizada correctamente.")


if __name__ == "__main__":
    anadir_usuarios()
