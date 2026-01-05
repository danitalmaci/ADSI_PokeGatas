class UserController:

    def __init__(self, db):
        self.db = db

    def create_user(self, nombre_usuario, nombre, apellido1, apellido2, correo_electronico, contrasena, fecha_nacimiento):
        if not nombre_usuario or not correo_electronico or len(contrasena) < 8:
            raise ValueError("Datos no válidos. Contraseña mínimo 8 caracteres.")

        self.db.insert(
            sentence="INSERT INTO users (nombre_usuario, nombre, apellido1, apellido2, correo_electronico, contrasena, fecha_nacimiento) VALUES (?, ?, ?, ?, ?, ?, ?)",
            parameters=[nombre_usuario.strip(), nombre.strip(), apellido1.strip(), apellido2.strip(), correo_electronico.strip(), contrasena.strip(), fecha_nacimiento]
        )

    def get_all(self):
        rows = self.db.select(
            sentence="SELECT * FROM users"
        )

        return [ dict(row) for row in rows ]