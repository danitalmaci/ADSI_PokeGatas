from app.controller.model.gestor_usuarios import GestorUsuarios
from app.controller.model.gestor_Pokemon import gestorPokemon 

class Pokedex:
    def __init__(self, db):
        self.db = db
        self.gestor_usuarios = GestorUsuarios(db)
        self.gestor_pokemon = gestorPokemon(db)

    # --- MÉTODOS DE USUARIOS (Intocables) ---
    def iniciar_sesion(self, nickname, contrasena):
        return self.gestor_usuarios.iniciarSesion(nickname, contrasena)
    def crear_cuenta(self, **kwargs):
        return self.gestor_usuarios.create_account(**kwargs)
    def consultar_perfil(self, nickname):
        return self.gestor_usuarios.consultar_perfil(nickname)
    def listar_usuarios(self):
        return self.gestor_usuarios.get_all()

    # --- MÉTODOS DE POKEDEX (¡RECUPERADOS!) ---
    # Estos son los que faltaban y daban error en la Home
    def mostrarPokedex(self):
        return self.gestor_pokemon.mostrarPokedex()

    def mostrarPokemon(self, nombrePokemon):
        return self.gestor_pokemon.mostrarPokemon(nombrePokemon)

    # --- MÉTODO DEL CHATBOT ---
    def solicitarConsultaCB(self, mensaje_usuario):
        # Delegamos la lógica al gestor
        return self.gestor_pokemon.procesar_mensaje_chatbot(mensaje_usuario)