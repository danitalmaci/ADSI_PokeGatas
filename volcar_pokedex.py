import requests
import time
import pokebase as pb
from app.database.connection import Connection 

TOTAL_POKEMONS = 151

def obtener_region(generacion):
    region_map = {
        "generation-i": "Kanto",
        "generation-ii": "Johto",
        "generation-iii": "Hoenn",
        "generation-iv": "Sinnoh",
        "generation-v": "Unova",
        "generation-vi": "Kalos",
        "generation-vii": "Alola",
        "generation-viii": "Galar",
        "generation-ix": "Paldea"
    }
    return region_map.get(generacion, "Desconocida")

def obtener_sexo(sexo_ratio):
    #Traduce el número de la API a texto.
    # -1: Sin género, 0: 100% Macho, 8: 100% Hembra, 1-7: Mixto
    if sexo_ratio == -1:
        return "Sin sexo"
    elif sexo_ratio == 0:
        return "Macho"
    elif sexo_ratio == 8:
        return "Hembra"
    return "Macho / Hembra"

# --- FUNCION PRINCIPAL --------------------

def seed_pokedex():
    print(f"Iniciando carga...")
    
    # instanciar la conexión a la base de datos
    db = Connection() 
    db.init_schema()  # Asegurarse de que se ha inicializado el esquema de la base de datos
    
    # limpiar tabla antes de insertar
    try:
        db.delete("DELETE FROM pokemon_pokedex") 
    except Exception as e:
        print(f"Nota: {e}")

    count = 0
    
    for poke_id in range(1, TOTAL_POKEMONS + 1):
        try:
            p = pb.pokemon(poke_id)
            s = pb.pokemon_species(poke_id)

            nombre = p.name.capitalize()

            try:
                imagen = p.sprites.other.official_artwork.front_default
            except:
                imagen = p.sprites.front_default

            altura = p.height / 10  # decímetros a metros
            peso = p.weight / 10    # hectogramos a kilogramos

            tipos_list = [t.type.name.capitalize() for t in p.types]
            tipos_str = "/".join(tipos_list)  # por ejemplo "Grass/Poison"

            stats = {s.stat.name: s.base_stat for s in p.stats} # Diccionario de stats, para no ir de uno en uno

            generacion = s.generation.name
            region = obtener_region(generacion)

            gender_rate = s.gender_rate
            sexo = obtener_sexo(gender_rate)
            
  
            query = """
                INSERT INTO pokemon_pokedex (
                    pokedex_id, nombre_pokemon, imagen, altura, peso, sexo,
                    ps, ataque, defensa, ataque_especial, defensa_especial, velocidad,
                    tipos, region
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                poke_id, 
                nombre, 
                imagen, 
                altura, 
                peso, 
                sexo,
                stats.get('hp', 0), 
                stats.get('attack', 0), 
                stats.get('defense', 0),
                stats.get('special-attack', 0), 
                stats.get('special-defense', 0), 
                stats.get('speed', 0),
                tipos_str, 
                region
            )
            
            db.insert(query, params)
            
            count += 1
            print(f"[{count}/{TOTAL_POKEMONS}] {nombre} insertado.")

        except Exception as e:
            print(f"Error en ID {poke_id}: {e}")

    print("Carga finalizada.")

if __name__ == "__main__":
    seed_pokedex()