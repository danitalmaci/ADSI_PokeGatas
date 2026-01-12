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
    def consultar_perfil(self, nickname: str) -> dict:
        return self.gestor_usuarios.consultar_perfil(nickname)

    # Cargar datos para la pantalla "Actualizar Perfil" (sql1)
    def get_datos_actualizar_perfil(self, nickname: str) -> dict:
        return self.gestor_usuarios.get_datos_actualizar_perfil(nickname)

    # Guardar cambios del perfil (sql2 + sql3)
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
    
    # -------- POKEDEX --------

    def mostrarPokedex(self):
        return self.gestor_Pokemon.mostrarPokedex()

    # -------- POKEMON --------

    def mostrarPokemon(self,nombrePokemon):
        return self.gestor_Pokemon.mostrarPokemon(nombrePokemon)
    
     # -------- NOTIFICACIONES --------

    def mostrarNotificaciones(self,nickname):
        return self.gestor_usuarios.mostrar_Notificaciones(nickname)

        

    # -------- SEGUIDORES --------
    # Ver seguidores (según diagrama 9.10)
    def cargar_seguidores(self, nickname_sesion: str) -> list:
        return self.gestor_usuarios.cargar_seguidores(nickname_sesion)

    # ✅ NUEVO: Eliminar seguidor (borrar relación en Sigue)
    def eliminar_seguidor(self, nickname_sesion: str, seguidor: str) -> bool:
        return self.gestor_usuarios.eliminar_seguidor(nickname_sesion, seguidor)
