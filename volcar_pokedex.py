import requests
import time
from app.database.connection import Connection 

TOTAL_POKEMONS = 1025 #todos

# hardcodeado porque no encuentro las descripciones ni imagenes en la API
INFO_REGIONES = {
    "Kanto": {"desc": "La primera región conocida, hogar de grandes investigadores.", "img": "static/img/regions/kanto.png"},
    "Johto": {"desc": "Una región rica en historia y tradiciones antiguas.", "img": "static/img/regions/johto.png"},
    "Hoenn": {"desc": "Conocida por su clima tropical y abundancia de agua.", "img": "static/img/regions/hoenn.png"},
    "Sinnoh": {"desc": "Una región montañosa llena de mitos sobre la creación.", "img": "static/img/regions/sinnoh.png"},
    "Unova": {"desc": "Una región moderna y urbana con gran diversidad.", "img": "static/img/regions/unova.png"},
    "Kalos": {"desc": "Famosa por su belleza, moda y la Megaevolución.", "img": "static/img/regions/kalos.png"},
    "Alola": {"desc": "Un archipiélago tropical con un ecosistema único.", "img": "static/img/regions/alola.png"},
    "Galar": {"desc": "Una región de vastas praderas e industrias potentes.", "img": "static/img/regions/galar.png"},
    "Paldea": {"desc": "Una vasta región conocida por el fenómeno de la Teracristalización.", "img": "static/img/regions/paldea.png"},
    "Desconocida": {"desc": "Origen desconocido.", "img": "static/img/regions/unknown.png"}
}

def obtener_region(generacion):
    region_map = {
        "generation-i": "Kanto", "generation-ii": "Johto", "generation-iii": "Hoenn",
        "generation-iv": "Sinnoh", "generation-v": "Unova", "generation-vi": "Kalos",
        "generation-vii": "Alola", "generation-viii": "Galar", "generation-ix": "Paldea"
    }
    return region_map.get(generacion, "Desconocida")

def obtener_sexo(sexo_ratio):
    # -1: Sin género, 0: 100% Macho, 8: 100% Hembra, 1-7: Mixto
    if sexo_ratio == -1: return "Sin sexo"
    if sexo_ratio == 0: return "Macho"
    if sexo_ratio == 8: return "Hembra"
    return "Macho / Hembra"

def obtener_descripcion_es(url, session):
    # Función auxiliar para sacar descripción en español de cualquier endpoint (move, ability)
    try:
        r = session.get(url)
        if r.status_code == 200:
            data = r.json()
            # flavor_text_entries para habilidades y movimientos
            entries = data.get('flavor_text_entries', [])
            for entry in entries:
                if entry['language']['name'] == 'es':
                    return data, entry['flavor_text'].replace('\n', ' ')
            
            # fallback ingles
            for entry in entries:
                if entry['language']['name'] == 'en':
                    return data, entry['flavor_text'].replace('\n', ' ')
        return None, "Sin descripción disponible."
    except:
        return None, "Error recuperando descripción."

# --- FUNCION PRINCIPAL --------------------

def seed_pokedex():
    print(f"Iniciando carga...")
    
    # instanciar la conexión a la base de datos
    db = Connection() 
    db.init_schema() 
    print("Base de datos conectada.")
   
    # limpiar tabla antes de insertar
    try:
        # borrar en orden por FKs
        db.delete("DELETE FROM AtacaCon")
        db.delete("DELETE FROM Posee")
        db.delete("DELETE FROM Contiene")
        db.delete("DELETE FROM PokemonPokedex")
        db.delete("DELETE FROM CategoriaPokemon")
        db.delete("DELETE FROM RegionPokemon")
        db.delete("DELETE FROM TipoPokemon") 
        db.delete("DELETE FROM AtaquePokemon")
        db.delete("DELETE FROM HabilidadPokemon")
    except Exception as e:
        print(f"Nota limpieza: {e}")

    session = requests.Session()
    count = 0
    
    # caches para evitar duplicados en tablas relacionadas y que tarde menos
    regiones_regs = set()
    tipos_regs = set()
    categorias_regs = set()
    habilidades_regs = set()
    ataques_regs = set()

    for poke_id in range(1, TOTAL_POKEMONS + 1):
        try:
            url_poke = f"https://pokeapi.co/api/v2/pokemon/{poke_id}/"
            r = session.get(url_poke)
            if r.status_code != 200:
                print(f"Error del ID {poke_id}: {r.status_code}")
                continue
            data = r.json()

            r_spec = session.get(data['species']['url'])
            s_data = r_spec.json() if r_spec.status_code == 200 else {}

            # --- DATOS BASICOS -------------------------------------------
            nombre = data['name'].capitalize()
            sprites = data['sprites']
            imagen = sprites.get('other', {}).get('official-artwork', {}).get('front_default') or sprites.get('front_default')
            altura = data['height'] / 10 
            peso = data['weight'] / 10 
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
            
            gen_name = s_data.get('generation', {}).get('name', '')
            region_nombre = obtener_region(gen_name)
            
            gender_rate = s_data.get('gender_rate', -1)
            sexo = obtener_sexo(gender_rate)

            # Prevolución
            pre_evo_data = s_data.get('evolves_from_species')
            if pre_evo_data:
                nombre_prevolucion = pre_evo_data['name'].capitalize()
            else:
                nombre_prevolucion = None

            # Categoría
            genera_list = s_data.get('genera', [])
            categoria_nombre = "Desconocida"
            for g in genera_list:
                if g['language']['name'] == 'es':
                    categoria_nombre = g['genus']
                    break
            if categoria_nombre == "Desconocida":
                 for g in genera_list:
                    if g['language']['name'] == 'en':
                        categoria_nombre = g['genus']
                        break

            # --- INSERTAR DATOS ---------------
            
            # region
            if region_nombre not in regiones_regs:
                info_reg = INFO_REGIONES.get(region_nombre, INFO_REGIONES["Desconocida"])
                db.insert("INSERT OR IGNORE INTO RegionPokemon (nombreRegion, descripcion, imagen) VALUES (?, ?, ?)", 
                          (region_nombre, info_reg["desc"], info_reg["img"]))
                regiones_regs.add(region_nombre)

            # categoria
            if categoria_nombre not in categorias_regs:
                desc_categoria = f"Clasificación biológica definida como {categoria_nombre}."
                db.insert("INSERT OR IGNORE INTO CategoriaPokemon (nombreCategoria, descripcion) VALUES (?, ?)", 
                          (categoria_nombre, desc_categoria))
                categorias_regs.add(categoria_nombre)

            # tipos
            tipos_data_list = data['types']
            nombres_tipos_actuales = [] 
            for t_obj in tipos_data_list:
                nombre_tipo = t_obj['type']['name'].capitalize()
                nombres_tipos_actuales.append(nombre_tipo)

                if nombre_tipo not in tipos_regs:
                    try:
                        r_tipo = session.get(t_obj['type']['url'])
                        if r_tipo.status_code == 200:
                            d_tipo = r_tipo.json()
                            debilidades = [w['name'].capitalize() for w in d_tipo['damage_relations']['double_damage_from']]
                            debilidades_str = ", ".join(debilidades)
                            imagen_tipo = f"static/img/types/{nombre_tipo}.png"
                            descripcion_tipo = f"Pokémon elemental de tipo {nombre_tipo}"
                            
                            db.insert("INSERT OR IGNORE INTO TipoPokemon (nombreTipo, descripcion, imagenTipo, debilidades) VALUES (?, ?, ?, ?)", 
                                      (nombre_tipo, descripcion_tipo, imagen_tipo, debilidades_str))
                        else:
                            db.insert("INSERT OR IGNORE INTO TipoPokemon (nombreTipo) VALUES (?)", (nombre_tipo,))
                    except:
                        db.insert("INSERT OR IGNORE INTO TipoPokemon (nombreTipo) VALUES (?)", (nombre_tipo,))
                    tipos_regs.add(nombre_tipo)

            # --- INSERTAR POKEMONS ------------------------------------------------
            query_poke = """
                INSERT INTO PokemonPokedex (
                    nombrePokemon, pokedexID, nombreRegion, nombreCategoria, nombrePokemonPrevolucion, imagen, 
                    altura, peso, sexo, ps, ataque, defensa, ataqueEspecial, defensaEspecial, velocidad
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params_poke = (
                nombre, poke_id, region_nombre, categoria_nombre, nombre_prevolucion, imagen, 
                altura, peso, sexo,
                stats.get('hp', 0), stats.get('attack', 0), stats.get('defense', 0),
                stats.get('special-attack', 0), stats.get('special-defense', 0), stats.get('speed', 0)
            )
            db.insert(query_poke, params_poke)

            # relacion Contiene
            for tipo in nombres_tipos_actuales:
                db.insert("INSERT INTO Contiene (nombrePokemon, nombreTipo) VALUES (?, ?)", (nombre, tipo))


            # --- HABILIDADES (Posee) ---------------------------------------
            for hab in data['abilities']:
                nombre_habilidad = hab['ability']['name'].replace('-', ' ').capitalize()
                
                # si es nueva, obtener descripción e insertar en tabla de todos
                if nombre_habilidad not in habilidades_regs:
                    url_hab = hab['ability']['url']
                    _, desc_hab = obtener_descripcion_es(url_hab, session)
                    
                    db.insert("INSERT OR IGNORE INTO HabilidadPokemon (nombreHabilidad, descripcion) VALUES (?, ?)", 
                              (nombre_habilidad, desc_hab))
                    habilidades_regs.add(nombre_habilidad)
                
                # insertar relacion Posee
                db.insert("INSERT INTO Posee (nombrePokemon, nombreHabilidad) VALUES (?, ?)", (nombre, nombre_habilidad))


            # --- ATAQUES (AtacaCon) ----------------------------------------
            for move in data['moves']:
                nombre_ataque = move['move']['name'].replace('-', ' ').capitalize()

                # s es nuevo, obtener detalles e insertar en tabla de todos
                if nombre_ataque not in ataques_regs:
                    url_move = move['move']['url']
                    move_json, desc_move = obtener_descripcion_es(url_move, session)
                    
                    poder = move_json.get('power') if move_json else None
                    precision = move_json.get('accuracy') if move_json else None
                    pp = move_json.get('pp') if move_json else None

                    db.insert("""
                        INSERT OR IGNORE INTO AtaquePokemon (nombreAtaque, descripcion, poder, precision, pp) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (nombre_ataque, desc_move, poder, precision, pp))
                    
                    ataques_regs.add(nombre_ataque)

                # insertar relacion AtacaCon
                db.insert("INSERT INTO AtacaCon (nombrePokemon, nombreAtaque) VALUES (?, ?)", (nombre, nombre_ataque))


            count += 1
            print(f"[{count}/{TOTAL_POKEMONS}] {nombre}", end='\r')

        except Exception as e:
            print(f"\nError en ID {poke_id}: {e}")

    print("\nCarga finalizada.")

if __name__ == "__main__":
    seed_pokedex()