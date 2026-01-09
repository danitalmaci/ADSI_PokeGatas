import requests
import time
from app.database.connection import Connection 

TOTAL_POKEMONS = 1025 #todos

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

    session = requests.Session()
    count = 0
    
    for poke_id in range(1, TOTAL_POKEMONS + 1):
        try:
            url_poke = f"https://pokeapi.co/api/v2/pokemon/{poke_id}/"
            r = session.get(url_poke)
            if r.status_code != 200:
                print(f"Error del ID {poke_id}: {r.status_code}")
                continue

            data = r.json()

            url_species = data['species']['url']
            r_spec = session.get(url_species)
            s_data = r_spec.json() if r_spec.status_code == 200 else {}

            nombre = data['name'].capitalize()

            sprites = data['sprites']
            other = sprites.get('other', {})
            official = other.get('official-artwork', {})
            imagen = official.get('front_default')
            
            if not imagen:
                imagen = sprites.get('front_default')

            altura = data['height'] / 10 
            peso = data['weight'] / 10 

            tipos_list = [t['type']['name'].capitalize() for t in data['types']]
            tipos_str = "/".join(tipos_list)

            # Stats: Lista de diccionarios -> Pasamos a Diccionario Clave:Valor
            # data['stats'] es [{'base_stat': 45, 'stat': {'name': 'hp'}}, ...]
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}


            generacion_name = s_data.get('generation', {}).get('name', '')
            region = obtener_region(generacion_name)

            gender_rate = s_data.get('gender_rate', -1)
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