class gestorPokemon:

    def __init__(self, db):
        self.db = db

    def mostrarPokedex(self):
        query = "SELECT pokedexID, nombrePokemon, imagen FROM PokemonPokedex"
        rows = self.db.select(query)
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