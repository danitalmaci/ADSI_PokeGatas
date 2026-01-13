from app.database.connection import Connection

class GestorEquipos:
    def __init__(self, db):
        self.db = db
    def obtener_equipos_usuario(self, user_id):
        # 1. Recuperamos los equipos del usuario
        sql_equipos = "SELECT id, nombre_equipo FROM equipos WHERE user_id = ?"
        rows = self.db.select(sql_equipos, [user_id])
        lista_equipos = [dict(row) for row in rows]
        # 2. Para cada equipo, recuperamos las imágenes de sus pokemons
        for equipo in lista_equipos:
            team_id = equipo['id']
            # Ajusta 'PokemonEquipo' si tu tabla se llama diferente
            sql_img = "SELECT imagen FROM PokemonEquipo WHERE equipo_id = ?"
            rows_img = self.db.select(sql_img, [team_id])
            # Guardamos las URLs en una lista simple
            equipo['imagenes'] = [row['imagen'] for row in rows_img]
            
        return lista_equipos
    
    def crear_equipo(self, id_usuario, nombre_equipo, lista_pok):
        if not nombre_equipo or not lista_pok:
            return False
            
        try:
            # 1. Insertar cabecera del equipo
            self.db.insert(
                sentence="INSERT INTO equipos (user_id, nombre_equipo) VALUES (?, ?)",
                parameters=[id_usuario, nombre_equipo] 
            )
            
            # 2. Obtener el ID generado
            rows = self.db.select("SELECT last_insert_rowid() as id")
            id_equipo_nuevo = rows[0]['id']

            # 3. Insertar los pokémon seleccionados copiando datos de la Pokedex (TU LÓGICA ORIGINAL)
            for id_pokemon in lista_pok:
                sql_insert = """
                    INSERT INTO PokemonEquipo (equipo_id, pokedex_id, nombre_pokemon, imagen, 
                                               altura, peso, sexo, ps, ataque, defensa, 
                                               ataque_especial, defensa_especial, velocidad)
                    SELECT ?, pokedexID, nombrePokemon, imagen, altura, peso, sexo, ps, 
                           ataque, defensa, ataqueEspecial, defensaEspecial, velocidad
                    FROM PokemonPokedex WHERE pokedexID = ?
                """
                self.db.insert(sql_insert, [id_equipo_nuevo, id_pokemon])
            
            return True

        except Exception as e:
            print(f"Error en crear_equipo: {e}")
            return False

    def eliminar_equipo(self, id_equipo):
        if not id_equipo:
            return False

        try:
            
            self.db.delete(
                sentence="DELETE FROM PokemonEquipo WHERE equipo_id = ?",
                parameters=[id_equipo]
            )

           
            self.db.delete(
                sentence="DELETE FROM equipos WHERE id = ?",
                parameters=[id_equipo]
            )
            return True
            
        except Exception as e:
            print(f"Error borrando equipo: {e}")
            return False
        
    def ver_detalle_equipo(self, nombre_equipo):
        try:
            sql = """
                SELECT p.nombre_pokemon, p.imagen 
                FROM PokemonEquipo p 
                JOIN equipos e ON p.equipo_id = e.id 
                WHERE e.nombre_equipo = ?
            """
            rows = self.db.select(sql, [nombre_equipo])

            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"Error en ver_detalle_equipo: {e}")
            return []
    
    def buscar_equipo(self, nombre):
        try:
            sql = "SELECT id, nombre_equipo FROM equipos WHERE nombre_equipo LIKE ?"
            rows = self.db.select(sql, [f"%{nombre}%"])
            
            resultados = []
            
            for row in rows:
                equipo = dict(row)
                sql_img = "SELECT imagen FROM PokemonEquipo WHERE equipo_id = ?"
                rows_img = self.db.select(sql_img, [equipo['id']])
                
                equipo['imagenes'] = [r['imagen'] for r in rows_img]
                resultados.append(equipo)
                
            return resultados

        except Exception as e:
            print(f"Error en buscar_equipo: {e}")
            return []
        
    def cargar_datos_equipo(self, id_equipo):
        try:
            sql = """
                SELECT pe.id as id_unico, e.nombre_equipo as NombreEquipo, 
                       pe.nombre_pokemon as NombrePokemon, 
                       pe.pokedex_id as idPokemon, pe.imagen 
                FROM equipos e 
                JOIN PokemonEquipo pe ON e.id = pe.equipo_id 
                WHERE e.id = ?
            """
            rows = self.db.select(sql, [id_equipo])
            
            detalle_equipo = []
            nombre_equipo = ""
            
            if rows:
                nombre_equipo = rows[0]['NombreEquipo']
            
            for row in rows:
                detalle_equipo.append({
                    "id_unico": row['id_unico'],
                    "nombrePokemon": row['NombrePokemon'],
                    "idPokemon": row['idPokemon'],
                    "imagen": row['imagen']
                })
            
            return {
                "id": id_equipo,
                "nombreEquipo": nombre_equipo,
                "pokemons": detalle_equipo
            }
            
        except Exception as e:
            print(f"Error cargar_datos_equipo: {e}")
            return None

    def eliminar_pokemon_de_equipo(self, id_unico):
        try:
            self.db.delete("DELETE FROM PokemonEquipo WHERE id = ?", [id_unico])
            return True
        except Exception:
            return False

    def insertar_pokemon_en_equipo(self, id_equipo, datos_poke):
        if self.contar_pokemons(id_equipo) >= 6: return False
        try:
            p = datos_poke
            sql = """
                INSERT INTO PokemonEquipo (equipo_id, pokedex_id, nombre_pokemon, imagen, 
                                           altura, peso, sexo, ps, ataque, defensa, 
                                           ataque_especial, defensa_especial, velocidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [
                id_equipo, p['pokedexID'], p['nombrePokemon'], p['imagen'],
                p.get('altura', 0), p.get('peso', 0), p.get('sexo', 'M'), p.get('ps', 0),
                p.get('ataque', 0), p.get('defensa', 0), p.get('ataqueEspecial', 0),
                p.get('defensaEspecial', 0), p.get('velocidad', 0)
            ]
            
            self.db.insert(sql, params)
            return True
            
        except Exception:
            return False
        
    def actualizar_nombre_equipo(self, id_equipo, nuevo_nombre):
        try:
            self.db.insert("UPDATE equipos SET nombre_equipo = ? WHERE id = ?", [nuevo_nombre, id_equipo])
            return True
        except Exception:
            return False
    
    def contar_pokemons(self, id_equipo):
        try:
            rows = self.db.select("SELECT COUNT(*) as total FROM PokemonEquipo WHERE equipo_id = ?", [id_equipo])
            return rows[0]['total'] if rows else 0
        except:
            return 0