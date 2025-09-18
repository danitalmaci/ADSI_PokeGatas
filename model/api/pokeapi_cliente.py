import pokebase as pb

class PokeApiCliente:
    def get_pokemon_por_nombre(self, nombre):
        return pb.pokemon(nombre)
    def get_pokemon_por_id(self, id):
        return pb.pokemon(id)
    def get_lista_pokemons(self, limit):
        return pb.APIResourceList('pokemon', limit)