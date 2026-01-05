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

CREATE TABLE IF NOT EXISTS pokemon_pokedex (
    pokedex_id INTEGER PRIMARY KEY, --el oficial
    nombre_pokemon TEXT NOT NULL,
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
    tipos TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nombre_equipo TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pokemon_equipo (
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
    FOREIGN KEY(pokedex_id) REFERENCES pokemon_pokedex(pokedex_id)
);