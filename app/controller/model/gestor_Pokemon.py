from flask import request
from flask import url_for
from app.database.connection import Connection
import unicodedata
import random

class gestorPokemon:
    def __init__(self, db):
        self.db = db

    def mostrarPokedex(self,):
        # Obtiene los valores de los filtros desde los parámetros de la URL (GET)
        # "nombre" se usa para filtrar por nombre de Pokémon
        filtroNombre = request.args.get("nombre")
        # "tipo" se usa para filtrar por tipo de Pokémon
        filtroTipo = request.args.get("tipo")

        # Consulta base para obtener los datos principales de la Pokédex
        # Se seleccionan el ID de la Pokédex, el nombre y la imagen del Pokémon
        # Se usan LEFT JOIN para que los Pokémon aparezcan aunque no tengan tipo asociado
        query = (
            "SELECT DISTINCT p.pokedexID, p.nombrePokemon, p.imagen "
            "FROM PokemonPokedex p "
            "LEFT JOIN Contiene t ON p.nombrePokemon = t.nombrePokemon "
            "LEFT JOIN TipoPokemon tp ON t.nombreTipo = tp.nombreTipo "
            "WHERE 1=1 "
        )
        # Lista donde se almacenan los valores de los filtros para la consulta
        params = []

        # Si se ha indicado un nombre, se filtra por nombre de Pokémon usando LIKE
        if filtroNombre:
            query += " AND p.nombrePokemon LIKE ?"
            params.append(f"%{filtroNombre}%")

        # Si se ha indicado un tipo, se filtra por tipo exacto
        if filtroTipo:
            query += " AND t.nombreTipo = ?"
            params.append(filtroTipo)

        # Ejecuta la consulta con los parámetros correspondientes
        rows = self.db.select(query, tuple(params))

        # Convierte cada fila del resultado en un diccionario y lo devuelve como lista
        return [dict(row) for row in rows]
    
    def mostrarPokemon(self, nombrePokemon):
        # Consulta para obtener toda la información detallada de un Pokémon concreto
        # Incluye datos generales, estadísticas, habilidades y tipos con su imagen
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

        # Ejecuta la consulta pasando el nombre del Pokémon como parámetro
        rows = self.db.select(query, (nombrePokemon,))

        # Si no se obtiene ningún resultado, se devuelve un diccionario vacío
        if not rows:
            return {}

        # Se toma la primera fila para obtener los datos generales del Pokémon
        base = rows[0]

        # Se crea la estructura base del JSON del Pokémon con sus datos principales
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
            # Listas vacías que luego se rellenarán con habilidades y tipos
            "habilidades": [],
            "tipos": []
        }

        # Estructuras auxiliares para evitar duplicados
        habilidades_set = set()   # Conjunto para habilidades únicas
        tipos_set = {}            # Diccionario para tipos únicos con su imagen

        # Recorre todas las filas devueltas para agrupar habilidades y tipos
        for row in rows:
            habilidades_set.add(row["nombreHabilidad"])
            tipos_set[row["nombreTipo"]] = row["imagenTipo"]

        # Convierte el conjunto de habilidades en una lista de diccionarios
        JSON_Pokemon["habilidades"] = [
            {"nombreHabilidad": h} for h in habilidades_set
        ]

        # Convierte el diccionario de tipos en una lista de diccionarios
        JSON_Pokemon["tipos"] = [
            {"nombreTipo": t, "imagenTipo": img}
            for t, img in tipos_set.items()
        ]

        # Devuelve el JSON final con toda la información del Pokémon
        return JSON_Pokemon

    
    def obtener_pokemon_por_id(self, pokedex_id):
        try:
            # Consultamos los datos necesarios para el equipo
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
