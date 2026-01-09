import requests
import time
from app.database.connection import Connection 

TOTAL_POKEMONS = 1025 #todos

# hardcodeado porque no encuentro las descripciones ni imagenes de las regiones en la API
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
    print("Base de datos conectada.")
   
    # limpiar tabla antes de insertar
    try:
        db.delete("DELETE FROM Contiene")
        db.delete("DELETE FROM PokemonPokedex")
        db.delete("DELETE FROM Categoria")
        db.delete("DELETE FROM RegionPokemon")
        db.delete("DELETE FROM TipoPokemon") 
    except Exception as e:
        print(f"Nota: {e}")

    session = requests.Session()
    count = 0
    
    # caches para evitar duplicados en tablas relacionadas
    regiones_regs = set()
    tipos_regs = set()
    categorias_regs = set()

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

            # --- PROCESAR DATOS ---------------------------------------------------
            nombre = data['name'].capitalize()
            
            # Imagen
            sprites = data['sprites']
            imagen = sprites.get('other', {}).get('official-artwork', {}).get('front_default') or sprites.get('front_default')
            # Medidas y Stats
            altura = data['height'] / 10 
            peso = data['weight'] / 10 
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
            
            # Datos de Especie
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
            
            # por si no encuentra en español
            if categoria_nombre == "Desconocida":
                 for g in genera_list:
                    if g['language']['name'] == 'en':
                        categoria_nombre = g['genus']
                        break

            # insertar región
            if region_nombre not in regiones_regs:
                info_reg = INFO_REGIONES.get(region_nombre, INFO_REGIONES["Desconocida"])
                
                db.insert("""
                    INSERT OR IGNORE INTO RegionPokemon (nombreRegion, descripcion, imagen) 
                    VALUES (?, ?, ?)
                """, (region_nombre, info_reg["desc"], info_reg["img"]))
                
                regiones_regs.add(region_nombre)

            # insertar categoría
            if categoria_nombre not in categorias_regs:
                # Generamos una descripción genérica basada en el nombre
                desc_categoria = f"Clasificación biológica definida como {categoria_nombre}."
                
                db.insert("""
                    INSERT OR IGNORE INTO Categoria (nombreCategoria, descripcion) 
                    VALUES (?, ?)
                """, (categoria_nombre, desc_categoria))
                
                categorias_regs.add(categoria_nombre)

            # insertar tipos con detalles (descripción, imagen, debilidades)
            tipos_data_list = data['types']
            nombres_tipos_actuales = [] # guardamos nombres para la tabla Contiene

            for t_obj in tipos_data_list:
                nombre_tipo = t_obj['type']['name'].capitalize()
                nombres_tipos_actuales.append(nombre_tipo)

                if nombre_tipo not in tipos_regs:
                    try:
                        # pedir detalles del tipo a la api
                        r_tipo = session.get(t_obj['type']['url'])
                        if r_tipo.status_code == 200:
                            d_tipo = r_tipo.json()
                            
                            # debilidades
                            debilidades = [w['name'].capitalize() for w in d_tipo['damage_relations']['double_damage_from']]
                            debilidades_str = ", ".join(debilidades)
                            
                            imagen_tipo = f"static/img/types/{nombre_tipo}.png"
                            descripcion_tipo = f"Pokémon elemental de tipo {nombre_tipo}"

                            db.insert("""
                                INSERT OR IGNORE INTO TipoPokemon (nombreTipo, descripcion, imagenTipo, debilidades) 
                                VALUES (?, ?, ?, ?)
                            """, (nombre_tipo, descripcion_tipo, imagen_tipo, debilidades_str))
                        else:
                            # fallback si falla la api del tipo
                            db.insert("INSERT OR IGNORE INTO TipoPokemon (nombreTipo) VALUES (?)", (nombre_tipo,))
                    
                    except:
                        db.insert("INSERT OR IGNORE INTO TipoPokemon (nombreTipo) VALUES (?)", (nombre_tipo,))
                    
                    tipos_regs.add(nombre_tipo)

            # insertar Pokémon en la tabla PokemonPokedex
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

            #relacion Contiene
            for tipo in nombres_tipos_actuales:
                db.insert("INSERT INTO Contiene (nombrePokemon, nombreTipo) VALUES (?, ?)", (nombre, tipo))

            count += 1
            print(f"[{count}/{TOTAL_POKEMONS}] {nombre}", end='\r')

        except Exception as e:
            print(f"Error en ID {poke_id}: {e}")

    print("Carga finalizada.")

if __name__ == "__main__":
    seed_pokedex()