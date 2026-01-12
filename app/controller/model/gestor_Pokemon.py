class gestorPokemon:

    def __init__(self, db):
        self.db = db

    def mostrarPokedex(self):
        query = "SELECT pokedexID, nombrePokemon, imagen FROM PokemonPokedex"
        rows = self.db.select(query)
        return [dict(row) for row in rows]
    
    def mostrarPokemon(self):
        query = "SELECT p.nombrePokemon, p.imagen,p.nombreCategoria p.altura, p.peso, p.pokedexID, p.sexo,"
        "p.ps, p.velocidad, p.ataque, p.ataqueEspecial, p.defensa, p.defensaEspecial, h.nombreHabilidad,"
        "t.imagenTipo FROM PokemonPokedex p INNER JOIN Posee h ON p.nombrePokemon = h.nombrePokemon "
        "INNER JOIN Contiene t ON p.nombrePokemon = t.nombrePokemon WHERE p.nombrePokemon = Pokemon"
        rows = self.db.select(query)
        return [dict(row) for row in rows]