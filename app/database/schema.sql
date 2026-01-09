/*esta tabla habria que revisar, es un  boceto */
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellido1 TEXT NOT NULL,
    apellido2 TEXT NOT NULL,
    foto TEXT,
    descripcion TEXT,
    contrasena TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    rol TEXT DEFAULT 'TRAINER',
    estado TEXT DEFAULT 'PENDIENTE' -- en el diagrama es un bool pero igual mejor asi para poder diferenciar entre aprobado, rechazado, pendiente
);

/* Tablas de la Pokedex */
/* -----------------------------------*/
CREATE TABLE IF NOT EXISTS RegionPokemon (
    nombreRegion TEXT PRIMARY KEY,
    descripcion TEXT,
    imagen TEXT
);

CREATE TABLE IF NOT EXISTS TipoPokemon (
    nombreTipo TEXT PRIMARY KEY,
    descripcion TEXT,
    imagenTipo TEXT,
    debilidades TEXT
);

CREATE TABLE IF NOT EXISTS HabilidadPokemon (
    nombreHabilidad TEXT PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS CategoriaPokemon (
    nombreCategoria TEXT PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS PokemonPokedex (
    pokedexID INTEGER PRIMARY KEY,

    nombreRegion TEXT,
    nombreCategoria TEXT,
    
    /* Atributos */
    nombrePokemon TEXT, 
    imagen TEXT,
    altura REAL,
    peso REAL,
    sexo TEXT,
    ps INTEGER,
    ataque INTEGER,
    defensa INTEGER,
    ataqueEspecial INTEGER,
    defensaEspecial INTEGER,
    velocidad INTEGER,
    nombrePokemonPrevolucion TEXT,
    
    FOREIGN KEY(nombreRegion) REFERENCES RegionPokemon(nombreRegion)
);

/* Relación Pokemon <-> Tipo) */
CREATE TABLE IF NOT EXISTS Contiene (
    nombrePokemon TEXT,
    nombreTipo TEXT,
    PRIMARY KEY (nombrePokemon, nombreTipo),
    FOREIGN KEY(nombrePokemon) REFERENCES PokemonPokedex(nombrePokemon),
    FOREIGN KEY(nombreTipo) REFERENCES TipoPokemon(nombreTipo)
);

/* Tabla con todas las habilidades */
CREATE TABLE IF NOT EXISTS HabilidadPokemon (
    nombreHabilidad TEXT PRIMARY KEY,
    descripcion TEXT
);

/* Relación Pokemon <-> Habilidad */
CREATE TABLE IF NOT EXISTS Posee (
    nombrePokemon TEXT,
    nombreHabilidad TEXT,
    PRIMARY KEY (nombrePokemon, nombreHabilidad),
    FOREIGN KEY(nombrePokemon) REFERENCES PokemonPokedex(nombrePokemon),
    FOREIGN KEY(nombreHabilidad) REFERENCES HabilidadPokemon(nombreHabilidad)
);

/* Tabla con todos los ataques */
CREATE TABLE IF NOT EXISTS AtaquePokemon (
    nombreAtaque TEXT PRIMARY KEY,
    descripcion TEXT,
    poder INTEGER,       /* Opcional: suele ser útil */
    precision INTEGER,   /* Opcional */
    pp INTEGER           /* Opcional */
);

/* Relación Pokemon <-> Ataque */
CREATE TABLE IF NOT EXISTS AtacaCon (
    nombrePokemon TEXT,
    nombreAtaque TEXT,
    PRIMARY KEY (nombrePokemon, nombreAtaque),
    FOREIGN KEY(nombrePokemon) REFERENCES PokemonPokedex(nombrePokemon),
    FOREIGN KEY(nombreAtaque) REFERENCES AtaquePokemon(nombreAtaque)
);

/* -----------------------------------*/

CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nombre_equipo TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
/* -----------------------------------*/


/*esta tabla habria que revisar, es un  boceto */
CREATE TABLE IF NOT EXISTS PokemonEquipo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_id INTEGER NOT NULL,
    pokedex_id INTEGER NOT NULL,
    nombre_pokemon TEXT, --mote
    imagen TEXT,
    altura REAL,
    peso REAL,
    sexo TEXT,
    ps INTEGER,
    ataque INTEGER,
    defensa INTEGER,
    ataque_especial INTEGER,
    defensa_especial INTEGER,
    velocidad INTEGER,
    nivel INTEGER, -- no se si vamos a guardarlo, imagino que si
    FOREIGN KEY(equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
    FOREIGN KEY(pokedex_id) REFERENCES Pokemon(pokedex_id)
);