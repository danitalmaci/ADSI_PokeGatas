class gestorPokemon:

    def __init__(self, db):
        self.db = db

    def mostrarPokedex(self, filtroNombre=None, filtroTipo=None, filtroHabilidad=None):
        query = (
            "SELECT DISTINCT p.pokedexID, p.nombrePokemon, p.imagen "
            "FROM PokemonPokedex p "
            "LEFT JOIN Posee h ON p.nombrePokemon = h.nombrePokemon "
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

        if filtroHabilidad:
            query += " AND h.nombreHabilidad = ?"
            params.append(filtroHabilidad)

        rows = self.db.select(query, tuple(params))

        return [dict(row) for row in rows]

    
    def mostrarPokemon(self,nombrePokemon):
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
        return [dict(row) for row in rows]