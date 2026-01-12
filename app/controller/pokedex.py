from app.controller.model.gestor_usuarios import GestorUsuarios

class Pokedex:
    def __init__(self, db):
        self.db = db
        self.gestor_usuarios = GestorUsuarios(db)

    def iniciar_sesion(self, nickname, contrasena) -> int:
        return self.gestor_usuarios.iniciarSesion(nickname, contrasena)

    def crear_cuenta(self, **kwargs):
        return self.gestor_usuarios.create_account(**kwargs)

    def consultar_perfil(self, nickname: str) -> dict:
        return self.gestor_usuarios.consultar_perfil(nickname)

    def listar_usuarios(self):
        return self.gestor_usuarios.get_all()
