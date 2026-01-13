from flask import request
from flask import url_for


class gestorPokemon:

    def __init__(self, db):
        self.db = db

    def mostrarPokedex(self,):
        filtroNombre = request.args.get("nombre")        # nombre o habilidad
        filtroTipo = request.args.get("tipo") 

        query = (
            "SELECT DISTINCT p.pokedexID, p.nombrePokemon, p.imagen "
            "FROM PokemonPokedex p "
            "LEFT JOIN Contiene t ON p.nombrePokemon = t.nombrePokemon "
            "LEFT JOIN TipoPokemon tp ON t.nombreTipo = tp.nombreTipo "
            "WHERE 1=1 "
        )
        params = []

        if filtroNombre:
            query += " AND p.nombrePokemon LIKE ?"
            params.append(f"%{filtroNombre}%")

        if filtroTipo:
            query += " AND t.nombreTipo = ?"
            params.append(filtroTipo)

        rows = self.db.select(query, tuple(params))

        return [dict(row) for row in rows]

    
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
            return {}  # Pokémon no encontrado
        
        # Tomamos los datos generales del Pokémon (la primera fila)
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
        
        # Agrupar habilidades
        habilidades_set = set()
        tipos_set = {}

        for row in rows:
            habilidades_set.add(row["nombreHabilidad"])
            tipos_set[row["nombreTipo"]] = row["imagenTipo"]
        
        # Convertir habilidades a lista de dicts
        JSON_Pokemon["habilidades"] = [{"nombreHabilidad": h} for h in habilidades_set]
        JSON_Pokemon["tipos"] = [{"nombreTipo": t, "imagenTipo": img} for t, img in tipos_set.items()]
        
        return JSON_Pokemon