class TeamController:

    def __init__(self, db):
        self.db = db

    
    def get_teams_by_user(self, user_id):

        rows = self.db.select(
            sentence="SELECT * FROM equipos WHERE user_id = ?",
            parameters=[user_id]
        )

        lista_equipos = [dict(row) for row in rows]
        for equipo in lista_equipos:
            # Asumiendo que la PK de equipos es 'id' (ajusta si es 'idEquipoPokemon')
            team_id = equipo['id'] 
            
            sql_img = "SELECT imagen FROM PokemonEquipo WHERE equipo_id = ?"
            rows_img = self.db.select(sql_img, [team_id])
            
            # 3. Guardamos solo las URLs de las imágenes en una lista nueva dentro del diccionario
            # Ejemplo: equipo['imagenes'] = ['/static/img/mew.png', '/static/img/pikachu.png']
            equipo['imagenes'] = [row['imagen'] for row in rows_img]

        return lista_equipos


    def consultarPokedex(self):
        
        return self.consultarPokedexCompleta()
    
    def consultarPokedexCompleta(self):
        query = "SELECT pokedexID, nombrePokemon, imagen FROM PokemonPokedex"
        rows = self.db.select(query)
        return [dict(row) for row in rows]
    
    def crearEquipo(self, nickname, nombreEquipo, lista_pok):
        return self.crearNuevoEquipo(nickname, nombreEquipo, lista_pok)

    def crearNuevoEquipo(self, nickname, nombreEquipo, lista_pok):
        if not nombreEquipo or not lista_pok:
            return False
            
        try:
            # Insertar cabecera del equipo
            self.db.insert(
                sentence="INSERT INTO equipos (user_id, nombre_equipo) VALUES (?, ?)",
                parameters=[nickname, nombreEquipo] 
            )
            
            # Obtener ID generado
            rows = self.db.select("SELECT last_insert_rowid() as id")
            id_equipo_nuevo = rows[0]['id']

            # Insertar los pokémon seleccionados copiando datos de la Pokedex
            for id_pokemon in lista_pok:
                sql_insert = """
                    INSERT INTO PokemonEquipo (equipo_id, pokedex_id, nombre_pokemon, imagen, 
                                               altura, peso, sexo, ps, ataque, defensa, 
                                               ataque_especial, defensa_especial, velocidad)
                    SELECT ?, pokedexID, nombrePokemon, imagen, altura, peso, sexo, ps, ataque, defensa, ataqueEspecial, defensaEspecial, velocidad
                    FROM PokemonPokedex WHERE pokedexID = ?
                """
                self.db.insert(sql_insert, [id_equipo_nuevo, id_pokemon])
            
            return True

        except Exception as e:
            print(f"Error en crearNuevoEquipo: {e}")
            return False

    def delete_team(self, team_id):
        if not team_id:
            return False

        try:
            
            self.db.delete(
                sentence="DELETE FROM PokemonEquipo WHERE equipo_id = ?",
                parameters=[team_id]
            )

           
            self.db.delete(
                sentence="DELETE FROM equipos WHERE id = ?",
                parameters=[team_id]
            )
            return True
            
        except Exception as e:
            print(f"Error borrando equipo: {e}")
            return False
        
    def verDetalleEquipo(self, nombreEquipo):
        # Adaptamos la query del flujo a tus tablas reales (equipos y PokemonEquipo)
        query = """
            SELECT p.nombre_pokemon, p.imagen 
            FROM PokemonEquipo p 
            JOIN equipos e ON p.equipo_id = e.id 
            WHERE e.nombre_equipo = ?
        """
        rows = self.db.select(sentence=query, parameters=[nombreEquipo])
        
        # Retornamos la lista (JSON Detalle Equipo)
        return [dict(row) for row in rows]