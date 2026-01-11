from werkzeug.security import generate_password_hash


class UserController:
    def __init__(self, db):
        self.db = db

    # Caso de uso: Registrarse
    # - valida datos
    # - comprueba nickname (sql1)
    # - comprueba correo (requisito de doc)
    # - inserta usuario (sql2) con rol=0 (pendiente)
    def create_account(self, nickname, nombre, apellido1, apellido2, correo, contrasena, fecha_nacimiento, descripcion=None, foto=None):
        nickname = (nickname or "").strip()
        nombre = (nombre or "").strip()
        apellido1 = (apellido1 or "").strip()
        apellido2 = (apellido2 or "").strip()
        correo = (correo or "").strip()
        contrasena = (contrasena or "").strip()
        descripcion = (descripcion or "").strip() if descripcion else None
        foto = (foto or "").strip() if foto else None

        # Validaciones mínimas (doc: contraseña mínimo 8 + campos obligatorios)
        if not nickname or not nombre or not apellido1 or not apellido2 or not correo or not fecha_nacimiento:
            raise ValueError("Datos no válidos. Rellena todos los campos obligatorios.")

        if len(contrasena) < 8:
            raise ValueError("Datos no válidos. Contraseña mínimo 8 caracteres.")

        # sql1: comprobar si existe nombreUsuario
        rows = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )
        if rows and rows[0]["cantidad"] > 0:
            raise ValueError("El nombre de usuario ya está en uso.")

        # (doc) comprobar si existe correo
        rows2 = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE correo = ?",
            parameters=[correo]
        )
        if rows2 and rows2[0]["cantidad"] > 0:
            raise ValueError("El correo ya está en uso.")

        # Guardar contraseña hasheada (coherente con anadir_usuarios.py)
        password_hash = generate_password_hash(contrasena)

        # sql2: insertar Usuario (rol=0 pendiente)
        self.db.insert(
            sentence="""
                INSERT INTO Usuario
                (nombreUsuario, nombre, apellido1, apellido2, foto, descripcion, contrasena, correo, fechaNacimiento, rol)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            parameters=[
                nickname,
                nombre,
                apellido1,
                apellido2,
                foto,
                descripcion,
                password_hash,
                correo,
                fecha_nacimiento
            ]
        )

    # Mantengo este método por si lo usas en admin/listado
    def get_all(self):
        rows = self.db.select(
            sentence="SELECT * FROM Usuario"
        )
        return [dict(row) for row in rows]
