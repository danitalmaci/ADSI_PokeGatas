# Pokedex MVC con Flask y SQLite

Pokedex para la asignatura de Análisis y Diseño de Sistemas de Información elaborado por el grupo **PokeGatas**, compuesto por:

* Daniel Talmaci
* June Castro
* Ivan Herrera
* Lou Marine Gomez
* David Miguez

## 📋 Descripción
Este proyecto implementa una aplicación web basada en el patrón de arquitectura **MVC (Modelo-Vista-Controlador)** utilizando Python, Flask y SQLite. Permite la gestión de usuarios, visualización de Pokémon, creación de equipos y administración del sistema.

Al iniciarla, se inicia automáticamente el volcado de la Pokedex a la base de datos, pero hemos subido los datos pre-cargados para poder usarla inmediatamente. Si se quiere revisar esa opción, borrar archivo *database.sqlite* y re-lanzar la Pokedex.

Requisitos: Python 3.12+, Flask y sqlite3.

##  Usuarios de Prueba

Para facilitar la corrección, se proporcionan los siguientes usuarios pre-cargados en la base de datos:

| Avatar | Rol | Usuario | Contraseña |
| :---: | :--- | :--- | :--- |
| <img src="app/static/img/usuario/user4.1.png" width="50"> | **Administrador** | `admin_jefe` | *admin123* |
| <img src="app/static/img/usuario/user3.1.png" width="50"> | **Entrenador** | `ash_ketchum` | *pikachu* |
