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
          - "lleno"   -> si ya tiene 6 y quiere añadir otro
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
       
        conteo = self.db.select(
            "SELECT COUNT(*) as total FROM PokemonFavoritos WHERE nombreUsuario = ?",
            [nickname]
        )
        total_favoritos = conteo[0]['total'] if conteo else 0


        if total_favoritos >= 6:
            return "lleno"


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


    # --- FUNCIONALIDAD 1: FORTALEZAS Y DEBILIDADES ---
    def _logica_fortalezas_debilidades(self, nombre_pokemon):
        sql_tipos = """SELECT t.nombreTipo FROM TipoPokemon t JOIN Contiene c ON t.nombreTipo = c.nombreTipo WHERE c.nombrePokemon = ?"""
        resultado_tipos = self.db.select(sql_tipos, (nombre_pokemon,))


        if not resultado_tipos:
            return {"error": "DATOS_FALTANTES", "msg": f"<b>{nombre_pokemon}</b> no tiene tipos registrados."}


        mis_tipos = [row['nombreTipo'] for row in resultado_tipos]
        lista_debilidades = set()
        for tipo_propio in mis_tipos:
            sql_debil = "SELECT debilidades FROM TipoPokemon WHERE nombreTipo = ?"
            res = self.db.select(sql_debil, (tipo_propio,))
            if res and res[0]['debilidades']:
                debs = res[0]['debilidades'].split(',')
                for d in debs: lista_debilidades.add(d.strip())


        lista_fortalezas = set()
        for tipo_propio in mis_tipos:
            sql_fort = "SELECT nombreTipo FROM TipoPokemon WHERE debilidades LIKE ?"
            res_fort = self.db.select(sql_fort, (f"%{tipo_propio}%",))
            for row in res_fort: lista_fortalezas.add(row['nombreTipo'])


        html_debilidades = self._generar_html_iconos(lista_debilidades)
        html_fortalezas = self._generar_html_iconos(lista_fortalezas)


        return {"error": None, "respuesta": f"Las debilidades de {nombre_pokemon} son:<br>{html_debilidades}<br><br>Las fortalezas de {nombre_pokemon} son:<br>{html_fortalezas}"}


    def _generar_html_iconos(self, lista_tipos):
        if not lista_tipos: return "Ninguna"
        traduccion_es = {'Electric': 'Eléctrico', 'Psychic': 'Psíquico', 'Fighting': 'Lucha', 'Flying': 'Volador', 'Ground': 'Tierra', 'Rock': 'Roca', 'Bug': 'Bicho', 'Ghost': 'Fantasma', 'Steel': 'Acero', 'Fire': 'Fuego', 'Water': 'Agua', 'Grass': 'Planta', 'Ice': 'Hielo', 'Dragon': 'Dragón', 'Dark': 'Siniestro', 'Fairy': 'Hada', 'Poison': 'Veneno', 'Normal': 'Normal'}
        html = "<div style='margin-top:10px; text-align: center; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;'>"
        for tipo in sorted(list(lista_tipos)):
            nombre_visual = traduccion_es.get(tipo, tipo).title()
            html += f"<div style='display: flex; flex-direction: column; align-items: center; width: 60px;'><img src='/static/img/type/type/{tipo}.png' style='width: 35px; height: 35px; margin-bottom: 5px;'><span style='font-size: 11px; color: white; font-weight: bold;'>{nombre_visual}</span></div>"
        html += "</div>"
        return html


    # --- FUNCIONALIDAD 2: EVOLUCIONES ---
    def _logica_evoluciones(self, nombre_pokemon):
        pre_evoluciones = []
        current_check = nombre_pokemon
        while True:
            sql = "SELECT nombrePokemonPrevolucion FROM PokemonPokedex WHERE nombrePokemon = ?"
            res = self.db.select(sql, (current_check,))
            if res and res[0]['nombrePokemonPrevolucion']:
                padre_nombre = res[0]['nombrePokemonPrevolucion']
                sql_img = "SELECT imagen FROM PokemonPokedex WHERE nombrePokemon = ?"
                res_img = self.db.select(sql_img, (padre_nombre,))
                imagen_padre = res_img[0]['imagen'] if res_img else ""
                pre_evoluciones.insert(0, {'nombre': padre_nombre, 'imagen': imagen_padre})
                current_check = padre_nombre
            else: break


        sql_actual = "SELECT imagen FROM PokemonPokedex WHERE nombrePokemon = ?"
        res_actual = self.db.select(sql_actual, (nombre_pokemon,))
        img_actual = res_actual[0]['imagen'] if res_actual else ""
        pokemon_actual = {'nombre': nombre_pokemon, 'imagen': img_actual}


        post_evoluciones = []
        def buscar_hijos_recursivo(nombre_padre):
            sql_hijos = "SELECT nombrePokemon, imagen FROM PokemonPokedex WHERE nombrePokemonPrevolucion = ?"
            hijos = self.db.select(sql_hijos, (nombre_padre,))
            for hijo in hijos:
                post_evoluciones.append({'nombre': hijo['nombrePokemon'], 'imagen': hijo['imagen']})
                buscar_hijos_recursivo(hijo['nombrePokemon'])
        buscar_hijos_recursivo(nombre_pokemon)


        linea_completa = pre_evoluciones + [pokemon_actual] + post_evoluciones
        nombre_bonito = nombre_pokemon.capitalize()
        return {"error": None, "respuesta": f"La línea evolutiva de {nombre_bonito} es la siguiente:<br>{self._generar_html_linea_evolutiva(linea_completa)}"}


    def _generar_html_linea_evolutiva(self, lista_pokemon):
        if not lista_pokemon: return "No hay datos."
        html = "<div style='margin-top:15px; text-align: center; display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 5px;'>"
        for index, poke in enumerate(lista_pokemon):
            html += f"<div style='display: flex; flex-direction: column; align-items: center; width: 80px;'><img src='{poke['imagen']}' style='width: 60px; height: 60px; object-fit: contain; margin-bottom: 5px;'><span style='font-size: 11px; color: white; font-weight: bold;'>{poke['nombre'].capitalize()}</span></div>"
            if index < len(lista_pokemon) - 1: html += "<div style='color: white; font-size: 20px; font-weight: bold;'>→</div>"
        html += "</div>"
        return html


    # --- FUNCIONALIDAD 3: REGIÓN ---
    def _logica_region(self, nombre_pokemon):
        sql = """SELECT r.nombreRegion FROM RegionPokemon r JOIN PokemonPokedex p ON r.nombreRegion = p.nombreRegion WHERE p.nombrePokemon = ?"""
        resultado = self.db.select(sql, (nombre_pokemon,))
        if not resultado:
            return {"error": "DATOS_FALTANTES", "msg": f"No encuentro la región de <b>{nombre_pokemon}</b>."}
        nombre_region = resultado[0]['nombreRegion']
        ruta_imagen_final = f"/static/img/regiones/regiones/{nombre_region}.png"
        nombre_pokemon_bonito = nombre_pokemon.capitalize()
        nombre_region_bonito = nombre_region.capitalize()
        respuesta_html = (
            f"La región de {nombre_pokemon_bonito} es:<br>"
            f"<div style='margin-top:15px; text-align: center; display: flex; flex-direction: column; align-items: center;'>"
            f"  <img src='{ruta_imagen_final}' alt='{nombre_region_bonito}' title='{nombre_region_bonito}' style='width: 250px; max-width: 100%; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>"
            f"  <span style='color: white; font-weight: bold; font-size: 16px;'>{nombre_region_bonito}</span>"
            f"</div>"
        )
        return {"error": None, "respuesta": respuesta_html}


    # --- FUNCIONALIDAD 4: COMPATIBILIDAD ---


    def _logica_amor(self, nombre1, nombre2):
        # 1. Obtener imágenes
        sql_img = "SELECT imagen FROM PokemonPokedex WHERE nombrePokemon = ?"
        res1 = self.db.select(sql_img, (nombre1,))
        img1 = res1[0]['imagen'] if res1 else ""
        res2 = self.db.select(sql_img, (nombre2,))
        img2 = res2[0]['imagen'] if res2 else ""


        # 2. Calcular Random
        porcentaje = random.randint(0, 100)


        # 3. Generar HTML
        respuesta_html = (
            f"La compatibilidad entre {nombre1} y {nombre2} es de:<br><br>"
            f"<div style='display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 10px;'>"
            f"  <div style='display: flex; flex-direction: column; align-items: center; width: 80px;'>"
            f"      <img src='{img1}' alt='{nombre1}' style='width: 70px; height: 70px; object-fit: contain;'>"
            f"      <span style='font-size: 11px; color: white; margin-top: 5px;'>{nombre1}</span>"
            f"  </div>"
            f"  <div style='width: 50px; height: 50px; background-color: white; border-radius: 50%; display: flex; justify-content: center; align-items: center; animation: heartbeat 1.5s infinite; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>"
            f"      <img src='/static/img/iconos/Imagen_Simbolo_Corazon.png' alt='Corazón' style='width: 35px;'>"
            f"  </div>"
            f"  <div style='display: flex; flex-direction: column; align-items: center; width: 80px;'>"
            f"      <img src='{img2}' alt='{nombre2}' style='width: 70px; height: 70px; object-fit: contain;'>"
            f"      <span style='font-size: 11px; color: white; margin-top: 5px;'>{nombre2}</span>"
            f"  </div>"
            f"</div>"
            f"<div style='text-align: center; font-size: 26px; font-weight: bold; color: white; margin-top: 15px;'>"
            f"  {porcentaje}%"
            f"</div>"
        )
        return {"error": None, "respuesta": respuesta_html}


