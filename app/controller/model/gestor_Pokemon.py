# app/controller/model/gestor_Pokemon.py
from flask import request
import unicodedata
import random
from volcar_pokedex import seed_pokedex


class gestorPokemon:
    def __init__(self, db):
        self.db = db

    # ==========================================
    #      MÉTODOS DE LA POKEDEX
    # ==========================================

    def mostrarPokedex(self, nickname: str = None):
        filtroNombre = request.args.get("nombre")
        filtroTipo = request.args.get("tipo")

        result = self.db.select("SELECT COUNT(*) AS total FROM PokemonPokedex")
        if result and result[0]["total"] == 0:
            seed_pokedex()
            return self.mostrarPokedex(nickname)

        params = []

        # ✅ Si hay usuario logueado, traemos "esFavorito"
        if nickname:
            query = (
                "SELECT DISTINCT p.pokedexID, p.nombrePokemon, p.imagen, "
                "CASE WHEN f.nombrePokemon IS NOT NULL THEN 1 ELSE 0 END AS esFavorito "
                "FROM PokemonPokedex p "
                "LEFT JOIN Contiene t ON p.nombrePokemon = t.nombrePokemon "
                "LEFT JOIN TipoPokemon tp ON t.nombreTipo = tp.nombreTipo "
                "LEFT JOIN PokemonFavoritos f "
                "  ON f.nombrePokemon = p.nombrePokemon AND f.nombreUsuario = ? "
                "WHERE 1=1 "
            )
            params.append(nickname)
        else:
            query = (
                "SELECT DISTINCT p.pokedexID, p.nombrePokemon, p.imagen, "
                "0 AS esFavorito "
                "FROM PokemonPokedex p "
                "LEFT JOIN Contiene t ON p.nombrePokemon = t.nombrePokemon "
                "LEFT JOIN TipoPokemon tp ON t.nombreTipo = tp.nombreTipo "
                "WHERE 1=1 "
            )

        if filtroNombre:
            query += " AND p.nombrePokemon LIKE ?"
            params.append(f"%{filtroNombre}%")

        if filtroTipo:
            query += " AND t.nombreTipo = ?"
            params.append(filtroTipo)

        rows = self.db.select(query, tuple(params))
        pokemons = [dict(row) for row in rows]

        # ✅ Normalizamos esFavorito a True/False (para Jinja)
        for p in pokemons:
            p["esFavorito"] = bool(p.get("esFavorito"))

        return pokemons

    def mostrarPokemon(self, nombrePokemon):
        query = (
            "SELECT p.nombrePokemon, p.imagen, p.nombreCategoria, p.altura, p.peso, "
            "p.pokedexID, p.sexo, p.ps, p.velocidad, p.ataque, p.ataqueEspecial, "
            "p.defensa, p.defensaEspecial, "
            "h.nombreHabilidad, "
            "t.nombreTipo, tp.imagenTipo "
            "FROM PokemonPokedex p "
            "INNER JOIN Posee h ON p.nombrePokemon = h.nombrePokemon "
            "INNER JOIN Contiene t ON p.nombrePokemon = t.nombrePokemon "
            "INNER JOIN TipoPokemon tp ON t.nombreTipo = tp.nombreTipo "
            "WHERE p.nombrePokemon = ?"
        )

        rows = self.db.select(query, (nombrePokemon,))
        if not rows:
            return {}

        base = rows[0]
        JSON_Pokemon = {
            "nombrePokemon": base["nombrePokemon"],
            "imagen": base["imagen"],
            "nombreCategoria": base["nombreCategoria"],
            "altura": base["altura"],
            "peso": base["peso"],
            "pokedexID": base["pokedexID"],
            "sexo": base["sexo"],
            "ps": base["ps"],
            "velocidad": base["velocidad"],
            "ataque": base["ataque"],
            "ataqueEspecial": base["ataqueEspecial"],
            "defensa": base["defensa"],
            "defensaEspecial": base["defensaEspecial"],
            "habilidades": [],
            "tipos": []
        }

        habilidades_set = set()
        tipos_set = {}

        for row in rows:
            habilidades_set.add(row["nombreHabilidad"])
            tipos_set[row["nombreTipo"]] = row["imagenTipo"]

        JSON_Pokemon["habilidades"] = [{"nombreHabilidad": h} for h in habilidades_set]
        JSON_Pokemon["tipos"] = [{"nombreTipo": t, "imagenTipo": img} for t, img in tipos_set.items()]

        return JSON_Pokemon

    def obtener_pokemon_por_id(self, pokedex_id):
        try:
            sql = """
                SELECT pokedexID, nombrePokemon, imagen, altura, peso, sexo, ps, 
                       ataque, defensa, ataqueEspecial, defensaEspecial, velocidad 
                FROM PokemonPokedex 
                WHERE pokedexID = ?
            """
            rows = self.db.select(sql, [pokedex_id])
            if rows:
                return dict(rows[0])
            return None
        except Exception as e:
            print(f"Error obtener_pokemon_por_id: {e}")
            return None

    # ==========================================
    # ⭐ FAVORITOS (TOGGLE)
    # ==========================================
    def toggle_favorito(self, nickname: str, nombrePokemon: str) -> str:
        """
        Devuelve:
          - "anadido" -> si se añadió
          - "quitado" -> si se quitó
        """
        nickname = (nickname or "").strip()
        nombrePokemon = (nombrePokemon or "").strip()

        if not nickname or not nombrePokemon:
            raise ValueError("Datos inválidos")

        # comprobar que el pokemon existe (por nombrePokemon)
        existe = self.db.select(
            "SELECT 1 FROM PokemonPokedex WHERE nombrePokemon = ? LIMIT 1",
            (nombrePokemon,)
        )
        if not existe:
            raise ValueError("Pokémon no encontrado")

        # si ya está, lo borramos
        ya = self.db.select(
            """
            SELECT 1
            FROM PokemonFavoritos
            WHERE nombreUsuario = ?
              AND nombrePokemon = ?
            LIMIT 1
            """,
            (nickname, nombrePokemon)
        )

        if ya:
            self.db.insert(
                """
                DELETE FROM PokemonFavoritos
                WHERE nombreUsuario = ?
                  AND nombrePokemon = ?
                """,
                (nickname, nombrePokemon)
            )
            return "quitado"

        # si no está, lo añadimos
        self.db.insert(
            """
            INSERT INTO PokemonFavoritos (nombreUsuario, nombrePokemon)
            VALUES (?, ?)
            """,
            (nickname, nombrePokemon)
        )
        return "anadido"

    # ==========================================
    #    MÉTODOS DEL CHATBOT 
    # ==========================================

    def limpiar_texto(self, texto):
        if not texto:
            return ""
        texto = texto.lower()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        texto = texto.replace("♀", "").replace("♂", "").replace("'", "").replace(".", "").replace(" ", "")
        return texto

    def buscar_nombre_real_inteligente(self, nombre_input):
        if not nombre_input:
            return None

        sql_directo = "SELECT nombrePokemon FROM PokemonPokedex WHERE lower(nombrePokemon) = lower(?)"
        res = self.db.select(sql_directo, (nombre_input.strip(),))
        if res:
            return res[0]['nombrePokemon']

        nombre_clean = self.limpiar_texto(nombre_input)
        sql_todos = "SELECT nombrePokemon FROM PokemonPokedex"
        todos = self.db.select(sql_todos)

        for fila in todos:
            nombre_db = fila['nombrePokemon']
            if self.limpiar_texto(nombre_db) == nombre_clean:
                return nombre_db
        return None

    def procesar_mensaje_chatbot(self, mensaje_usuario):
        try:
            if not mensaje_usuario:
                return {"error": "VACIO", "msg": "No has escrito nada."}

            partes = mensaje_usuario.split('-')
            if len(partes) < 2:
                return {"error": "FORMATO_INVALIDO", "msg": "Formato incorrecto. Recuerda usar: <b>Num-Nombre</b>"}

            opcion = partes[0].strip()

            if opcion in ['1', '2', '3']:
                if len(partes) != 2 or not partes[1].strip():
                    return {"error": "FORMATO_INVALIDO", "msg": f"La opción {opcion} requiere: <b>{opcion}-Pokemon</b>"}
                nombre_raw = partes[1].strip()
                return self.generarRespuestaCB(opcion, nombre_raw)

            elif opcion == '4':
                if len(partes) != 3 or not partes[1].strip() or not partes[2].strip():
                    return {"error": "FORMATO_INVALIDO", "msg": "La opción 4 requiere: <b>4-Pokemon1-Pokemon2</b>"}
                nombre1 = partes[1].strip()
                nombre2 = partes[2].strip()
                return self.generarRespuestaCB(opcion, nombre1, nombre2)

            else:
                return {"error": "OPCION_INVALIDA", "msg": f"La opción <b>{opcion}</b> no existe."}

        except Exception as e:
            print(f"ERROR GESTOR: {e}")
            return {"error": "SERVER_ERROR", "msg": "Error procesando tu solicitud."}

    def generarRespuestaCB(self, opcion, nombre1, nombre2=None):
        nombre_real_1 = self.buscar_nombre_real_inteligente(nombre1)
        if not nombre_real_1:
            return {"error": "NO_ENCONTRADO", "msg": f"No encuentro a <b>{nombre1}</b>. Revisa el nombre."}

        nombre_bonito_1 = nombre_real_1.capitalize()

        if opcion == '1':
            return self._logica_fortalezas_debilidades(nombre_bonito_1)
        elif opcion == '2':
            return self._logica_evoluciones(nombre_real_1)
        elif opcion == '3':
            return self._logica_region(nombre_real_1)
        elif opcion == '4':
            nombre_real_2 = self.buscar_nombre_real_inteligente(nombre2)
            if not nombre_real_2:
                return {"error": "NO_ENCONTRADO", "msg": f"No encuentro a <b>{nombre2}</b>."}
            nombre_bonito_2 = nombre_real_2.capitalize()
            return self._logica_amor(nombre_bonito_1, nombre_bonito_2)

        return {"error": "ERROR", "msg": "Opción no gestionada."}

    # (resto chatbot igual...)
    # ... (tu código de fortalezas/evoluciones/región/amor se queda igual)
