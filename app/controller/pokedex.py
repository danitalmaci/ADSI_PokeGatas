from app.controller.model.gestor_usuarios import GestorUsuarios
from app.controller.model.gestor_Pokemon import gestorPokemon


class Pokedex:
    def __init__(self, db):
        self.db = db
        self.gestor_usuarios = GestorUsuarios(db)
        self.gestor_Pokemon = gestorPokemon(db)

    # -------- USUARIOS / AUTH --------
    def iniciar_sesion(self, nickname, contrasena) -> int:
        return self.gestor_usuarios.iniciarSesion(nickname, contrasena)

    def crear_cuenta(self, **kwargs):
        return self.gestor_usuarios.create_account(**kwargs)

    def listar_usuarios(self):
        return self.gestor_usuarios.get_all()

    # -------- PERFIL --------
    # ✅ IMPORTANTE: ahora acepta viewer para saber si "yo" sigo a ese perfil
    def consultar_perfil(self, nickname: str, viewer: str = None) -> dict:
        return self.gestor_usuarios.consultar_perfil(nickname, viewer=viewer)

    # Cargar datos para la pantalla "Actualizar Perfil"
    def get_datos_actualizar_perfil(self, nickname: str) -> dict:
        return self.gestor_usuarios.get_datos_actualizar_perfil(nickname)

    # Guardar cambios del perfil
    def actualizar_datos_perfil(
        self,
        nickname_sesion: str,
        nuevo_nickname: str,
        nombre: str,
        apellido1: str,
        apellido2: str,
        descripcion: str,
        fecha_nacimiento: str,
        correo: str,
        foto: str = None
    ):
        return self.gestor_usuarios.actualizar_datos(
            nickname_sesion=nickname_sesion,
            nuevo_nickname=nuevo_nickname,
            nombre=nombre,
            apellido1=apellido1,
            apellido2=apellido2,
            descripcion=descripcion,
            fecha_nacimiento=fecha_nacimiento,
            correo=correo,
            foto=foto
        )

    # -------- SEGUIR / COMPROBAR SEGUIR --------
    # ✅ seguir usuario
    def seguir_usuario(self, nickname_sesion: str, nickname_objetivo: str) -> bool:
        return self.gestor_usuarios.seguir_usuario(nickname_sesion, nickname_objetivo)

    # ✅ dejar de seguir usuario
    def dejar_seguir_usuario(self, nickname_sesion: str, nickname_objetivo: str) -> bool:
        return self.gestor_usuarios.dejar_seguir_usuario(nickname_sesion, nickname_objetivo)

    # ✅ comprobar si ya le sigue (en tu gestor se llama le_sigue)
    def ya_sigo_a(self, nickname_sesion: str, nickname_objetivo: str) -> bool:
        return self.gestor_usuarios.le_sigue(nickname_sesion, nickname_objetivo)

    # -------- POKEDEX --------
    def mostrarPokedex(self):
        return self.gestor_Pokemon.mostrarPokedex()

    # -------- POKEMON --------
    def mostrarPokemon(self, nombrePokemon):
        return self.gestor_Pokemon.mostrarPokemon(nombrePokemon)

    # -------- NOTIFICACIONES --------
    def mostrarNotificaciones(self, nickname):
        return self.gestor_usuarios.mostrar_Notificaciones(nickname)

    # -------- SEGUIDORES --------
    def cargar_seguidores(self, nickname_sesion: str) -> list:
        return self.gestor_usuarios.cargar_seguidores(nickname_sesion)

    def eliminar_seguidor(self, nickname_sesion: str, seguidor: str) -> bool:
        return self.gestor_usuarios.eliminar_seguidor(nickname_sesion, seguidor)

    # -------- SEGUIDOS --------
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
