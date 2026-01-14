from app.controller.model.gestor_usuarios import GestorUsuarios
from app.controller.model.gestor_Pokemon import gestorPokemon
from app.controller.model.gestor_equipos import GestorEquipos

class Pokedex:
    def __init__(self, db):
        self.db = db
        self.gestor_usuarios = GestorUsuarios(db)
        # --- CORRECCIÓN AQUÍ: P mayúscula a p minúscula ---
        self.gestor_pokemon = gestorPokemon(db) 
        # --------------------------------------------------
        self.gestor_equipos = GestorEquipos(db)

    # -------- USUARIOS / AUTH --------
    def iniciar_sesion(self, nickname, contrasena) -> int:
        return self.gestor_usuarios.iniciarSesion(nickname, contrasena)
    def crear_cuenta(self, **kwargs):
        return self.gestor_usuarios.create_account(**kwargs)
    def consultar_perfil(self, nickname, viewer: str = None) -> dict:
        return self.gestor_usuarios.consultar_perfil(nickname, viewer=viewer)
    def listar_usuarios(self):
        return self.gestor_usuarios.get_all()

    # -------- PERFIL --------
    def get_datos_actualizar_perfil(self, nickname: str) -> dict:
        return self.gestor_usuarios.get_datos_actualizar_perfil(nickname)

    def actualizar_datos_perfil(self, nickname_sesion: str, nuevo_nickname: str, nombre: str, apellido1: str, apellido2: str, descripcion: str, fecha_nacimiento: str, correo: str, foto: str = None):
        return self.gestor_usuarios.actualizar_datos(nickname_sesion=nickname_sesion, nuevo_nickname=nuevo_nickname, nombre=nombre, apellido1=apellido1, apellido2=apellido2, descripcion=descripcion, fecha_nacimiento=fecha_nacimiento, correo=correo, foto=foto)

    # -------- SEGUIR / COMPROBAR SEGUIR --------
    def seguir_usuario(self, nickname_sesion: str, nickname_objetivo: str) -> bool:
        return self.gestor_usuarios.seguir_usuario(nickname_sesion, nickname_objetivo)

    def dejar_seguir_usuario(self, nickname_sesion: str, nickname_objetivo: str) -> bool:
        return self.gestor_usuarios.dejar_seguir_usuario(nickname_sesion, nickname_objetivo)

    def ya_sigo_a(self, nickname_sesion: str, nickname_objetivo: str) -> bool:
        return self.gestor_usuarios.le_sigue(nickname_sesion, nickname_objetivo)

    # -------- POKEDEX --------
    def mostrarPokedex(self):
        # Aquí también hay que usar la minúscula corregida
        return self.gestor_pokemon.mostrarPokedex()

    # -------- POKEMON --------
    def mostrarPokemon(self, nombrePokemon):
        return self.gestor_pokemon.mostrarPokemon(nombrePokemon)

    def obtener_pokemon_por_id(self, pokedex_id):
        return self.gestor_pokemon.obtener_pokemon_por_id(pokedex_id)

     # -------- NOTIFICACIONES --------
    def mostrarNotificaciones(self,nickname):
        return self.gestor_usuarios.mostrar_Notificaciones(nickname)

    def crear_notificacion(self, nickname, mensaje):
        return self.gestor_usuarios.crear_notificacion(nickname, mensaje)

    # -------- SEGUIDORES / SEGUIDOS --------
    def cargar_seguidores(self, nickname_sesion: str) -> list:
        return self.gestor_usuarios.cargar_seguidores(nickname_sesion)

    def eliminar_seguidor(self, nickname_sesion: str, seguidor: str) -> bool:
        return self.gestor_usuarios.eliminar_seguidor(nickname_sesion, seguidor)

    def cargar_seguidos(self, nickname_sesion: str) -> list:
        return self.gestor_usuarios.cargar_seguidos(nickname_sesion)

    def eliminar_seguido(self, nickname_sesion: str, seguido: str) -> bool:
        return self.gestor_usuarios.eliminar_seguido(nickname_sesion, seguido)

    # -------- ADMIN --------
    def obtenerCuentas(self, filtro_nombre=None):
        return self.gestor_usuarios.obtenerCuentas(filtro_nombre)

    def obtenerCuentasPendientes(self):
        return self.gestor_usuarios.obtenerCuentasPendientes()

    def aprobarCuenta(self, nickname):
        return self.gestor_usuarios.aprobarCuenta(nickname)
    
    def borrarCuenta(self, nickname):
        return self.gestor_usuarios.borrarCuenta(nickname)

    def modificarCuenta(self, **kwargs):
        return self.gestor_usuarios.update_user_admin(**kwargs)

    # -------- EQUIPOS --------
    def obtener_equipos_usuario(self, user_id):
        return self.gestor_equipos.obtener_equipos_usuario(user_id)
    
    def eliminar_equipo(self, id_equipo):
        return self.gestor_equipos.eliminar_equipo(id_equipo)
    
    def crear_equipo(self, id_usuario, nombre_equipo, lista_ids):
        return self.gestor_equipos.crear_equipo(id_usuario, nombre_equipo, lista_ids)
    
    def buscar_equipo(self, nombre):
        return self.gestor_equipos.buscar_equipo(nombre)

    def ver_detalle_equipo(self, nombre_equipo):
            return self.gestor_equipos.ver_detalle_equipo(nombre_equipo)
    
    def cargar_datos_equipo(self, id_equipo):
        return self.gestor_equipos.cargar_datos_equipo(id_equipo)

    def actualizar_nombre_equipo(self, id_equipo, nuevo_nombre):
        return self.gestor_equipos.actualizar_nombre_equipo(id_equipo, nuevo_nombre)

    def eliminar_pokemon_de_equipo(self, id_unico):
        return self.gestor_equipos.eliminar_pokemon_de_equipo(id_unico)

    def insertar_pokemon_en_equipo(self, id_equipo, datos):
        return self.gestor_equipos.insertar_pokemon_en_equipo(id_equipo, datos)

    def contar_pokemons(self, id_equipo):
        return self.gestor_equipos.contar_pokemons(id_equipo)

    # --- MÉTODO DEL CHATBOT ---
    def solicitarConsultaCB(self, mensaje_usuario):
        # Delegamos la lógica al gestor (ahora coincide con el init)
        return self.gestor_pokemon.procesar_mensaje_chatbot(mensaje_usuario)