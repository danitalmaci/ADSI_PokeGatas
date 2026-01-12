# app/controller/model/gestor_usuarios.py
from werkzeug.security import generate_password_hash, check_password_hash


class GestorUsuarios:
    def __init__(self, db):
        self.db = db

    # -------------------------------------------------
    # Caso de uso: Iniciar sesión
    # -------------------------------------------------
    def iniciarSesion(self, nickname, contrasena) -> int:
        nickname = (nickname or "").strip()
        contrasena = (contrasena or "").strip()

        if not nickname or not contrasena:
            return 0

        rows = self.db.select(
            sentence="""
                SELECT contrasena
                FROM Usuario
                WHERE nombreUsuario = ?
            """,
            parameters=[nickname]
        )

        if not rows:
            return 0

        password_hash = rows[0]["contrasena"]

        if check_password_hash(password_hash, contrasena):
            return 1

        return 0

    # -------------------------------------------------
    # Caso de uso: Registrarse
    # -------------------------------------------------
    def create_account(
        self,
        nickname,
        nombre,
        apellido1,
        apellido2,
        correo,
        contrasena,
        fecha_nacimiento,
        descripcion=None,
        foto=None
    ):
        nickname = (nickname or "").strip()
        nombre = (nombre or "").strip()
        apellido1 = (apellido1 or "").strip()
        apellido2 = (apellido2 or "").strip()
        correo = (correo or "").strip()
        contrasena = (contrasena or "").strip()
        descripcion = (descripcion or "").strip() if descripcion else None
        foto = (foto or "").strip() if foto else None

        if not nickname or not nombre or not apellido1 or not apellido2 or not correo or not fecha_nacimiento:
            raise ValueError("Datos no válidos. Rellena todos los campos obligatorios.")

        if len(contrasena) < 8:
            raise ValueError("Datos no válidos. Contraseña mínimo 8 caracteres.")

        # comprobar nickname
        rows = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )
        if rows and rows[0]["cantidad"] > 0:
            raise ValueError("El nombre de usuario ya está en uso.")

        # comprobar correo
        rows2 = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE correo = ?",
            parameters=[correo]
        )
        if rows2 and rows2[0]["cantidad"] > 0:
            raise ValueError("El correo ya está en uso.")

        password_hash = generate_password_hash(contrasena)

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

    # -------------------------------------------------
    # Caso de uso: Consultar perfil (doc 9.8)
    # -------------------------------------------------
    def consultar_perfil(self, nickname: str) -> dict:
        nickname = (nickname or "").strip()
        if not nickname:
            raise ValueError("Nickname vacío")

        rows_user = self.db.select(
            sentence="SELECT nombreUsuario, foto FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )

        if not rows_user:
            raise ValueError("Usuario no encontrado")

        user_row = dict(rows_user[0])

        seguidores = 0
        seguidos = 0

        try:
            rows_followers = self.db.select(
                sentence="SELECT COUNT(*) AS numero_seguidores FROM Sigue WHERE nombreUsuarioSeguido = ?",
                parameters=[nickname]
            )
            seguidores = rows_followers[0]["numero_seguidores"]
        except Exception:
            seguidores = 0

        try:
            rows_following = self.db.select(
                sentence="SELECT COUNT(*) AS numero_seguidos FROM Sigue WHERE nombreUsuarioSeguidor = ?",
                parameters=[nickname]
            )
            seguidos = rows_following[0]["numero_seguidos"]
        except Exception:
            seguidos = 0

        return {
            "nickname": user_row["nombreUsuario"],
            "foto": user_row.get("foto"),
            "numero_seguidores": int(seguidores),
            "numero_seguidos": int(seguidos),
        }

    # -------------------------------------------------
    # sql1: Cargar datos para la pantalla "Actualizar Perfil"
    # -------------------------------------------------
    def get_datos_actualizar_perfil(self, nickname: str) -> dict:
        nickname = (nickname or "").strip()
        if not nickname:
            raise ValueError("Nickname vacío")

        rows = self.db.select(
            sentence="""
                SELECT nombreUsuario, nombre, apellido1, apellido2, correo, fechaNacimiento, descripcion, foto
                FROM Usuario
                WHERE nombreUsuario = ?
            """,
            parameters=[nickname]
        )

        if not rows:
            raise ValueError("Usuario no encontrado")

        row = dict(rows[0])

        return {
            "nickname": row.get("nombreUsuario"),
            "nombre": row.get("nombre"),
            "apellido1": row.get("apellido1"),
            "apellido2": row.get("apellido2"),
            "correo": row.get("correo"),
            "fecha_nacimiento": row.get("fechaNacimiento"),
            "descripcion": row.get("descripcion"),
            "foto": row.get("foto"),
        }

    # -------------------------------------------------
    # sql2: comprobarNicknameRepe
    # -------------------------------------------------
    def comprobar_nickname_repe(self, nickname: str) -> int:
        rows = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )
        if not rows:
            return 0
        return int(rows[0]["cantidad"])

    # -------------------------------------------------
    # sql3: actualizarDatos
    # -------------------------------------------------
    def actualizar_datos(
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
    ) -> bool:
        nickname_sesion = (nickname_sesion or "").strip()
        nuevo_nickname = (nuevo_nickname or "").strip()

        if not nickname_sesion or not nuevo_nickname:
            raise ValueError("Nickname vacío")

        # sql2 solo si cambia el nickname
        if nuevo_nickname != nickname_sesion:
            if self.comprobar_nickname_repe(nuevo_nickname) > 0:
                raise ValueError("El nombre de usuario ya está en uso.")

        self.db.update(
            sentence="""
                UPDATE Usuario
                SET nombreUsuario = ?, nombre = ?, apellido1 = ?, apellido2 = ?, correo = ?, fechaNacimiento = ?, descripcion = ?, foto = ?
                WHERE nombreUsuario = ?
            """,
            parameters=[
                nuevo_nickname,
                nombre,
                apellido1,
                apellido2,
                correo,
                fecha_nacimiento,
                descripcion,
                foto,
                nickname_sesion
            ]
        )
        return True

    # -------------------------------------------------
    # Caso de uso: Ver seguidores (doc 9.10)
    # Devuelve JSON = [ { nombreUsuarioSeguidor, fotoSeguidor,
    #                     numSeguidoresDelSeguidor, numSeguidosDelSeguidor }, ... ]
    # -------------------------------------------------
    def cargar_seguidores(self, nickname_sesion: str) -> list:
        nickname_sesion = (nickname_sesion or "").strip()
        if not nickname_sesion:
            raise ValueError("Nickname vacío")

        # sql1
        rows = self.db.select(
            sentence="""
                SELECT nombreUsuarioSeguidor
                FROM Sigue
                WHERE nombreUsuarioSeguido = ?
            """,
            parameters=[nickname_sesion]
        )

        seguidores_json = []

        for r in rows:
            nickname_seguidor = r["nombreUsuarioSeguidor"]

            # sql2
            row_foto = self.db.select(
                sentence="""
                    SELECT foto
                    FROM Usuario
                    WHERE nombreUsuario = ?
                """,
                parameters=[nickname_seguidor]
            )
            foto_seguidor = row_foto[0]["foto"] if row_foto else None

            # sql3
            row_num_seguidores = self.db.select(
                sentence="""
                    SELECT COUNT(*) AS numero_seguidores
                    FROM Sigue
                    WHERE nombreUsuarioSeguido = ?
                """,
                parameters=[nickname_seguidor]
            )
            num_seguidores = int(row_num_seguidores[0]["numero_seguidores"]) if row_num_seguidores else 0

            # sql4
            row_num_seguidos = self.db.select(
                sentence="""
                    SELECT COUNT(*) AS numero_seguidos
                    FROM Sigue
                    WHERE nombreUsuarioSeguidor = ?
                """,
                parameters=[nickname_seguidor]
            )
            num_seguidos = int(row_num_seguidos[0]["numero_seguidos"]) if row_num_seguidos else 0

            seguidores_json.append({
                "nombreUsuarioSeguidor": nickname_seguidor,
                "fotoSeguidor": foto_seguidor,
                "numSeguidoresDelSeguidor": num_seguidores,
                "numSeguidosDelSeguidor": num_seguidos
            })

        return seguidores_json

    # -------------------------------------------------
    # ✅ NUEVO: eliminar seguidor (borrar relación en Sigue)
    # nickname_sesion = tú (seguidO)
    # seguidor = quien te sigue (seguidor)
    # -------------------------------------------------
    def eliminar_seguidor(self, nickname_sesion: str, seguidor: str) -> bool:
        nickname_sesion = (nickname_sesion or "").strip()
        seguidor = (seguidor or "").strip()

        if not nickname_sesion or not seguidor:
            raise ValueError("Datos inválidos")

        self.db.delete(
            sentence="""
                DELETE FROM Sigue
                WHERE nombreUsuarioSeguido = ?
                  AND nombreUsuarioSeguidor = ?
            """,
            parameters=[nickname_sesion, seguidor]
        )
        return True

    # -------------------------------------------------
    # Listado
    # -------------------------------------------------
    def get_all(self):
        rows = self.db.select(sentence="SELECT * FROM Usuario")
        return [dict(row) for row in rows]
