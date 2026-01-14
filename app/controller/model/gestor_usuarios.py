# app/controller/model/gestor_usuarios.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
import datetime

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
            sentence="SELECT contrasena, rol FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )

        if not rows:
            return 0

        usuario = rows[0]
        password_hash = usuario["contrasena"]
        rol = usuario["rol"]
        if check_password_hash(password_hash, contrasena):
            if rol == 0:
                return -1 
            
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

        rows = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )
        if rows and rows[0]["cantidad"] > 0:
            raise ValueError("El nombre de usuario ya está en uso.")

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
    # ✅ comprobar si "viewer" sigue a "target"
    # -------------------------------------------------
    def le_sigue(self, viewer: str, target: str) -> bool:
        viewer = (viewer or "").strip()
        target = (target or "").strip()
        if not viewer or not target or viewer == target:
            return False

        rows = self.db.select(
            sentence="""
                SELECT 1
                FROM Sigue
                WHERE nombreUsuarioSeguido = ?
                  AND nombreUsuarioSeguidor = ?
                LIMIT 1
            """,
            parameters=[target, viewer]
        )
        return bool(rows)

    # -------------------------------------------------
    # ✅ seguir usuario
    # -------------------------------------------------
    def seguir_usuario(self, viewer: str, target: str) -> bool:
        viewer = (viewer or "").strip()
        target = (target or "").strip()

        if not viewer or not target:
            raise ValueError("Datos inválidos")
        if viewer == target:
            raise ValueError("No puedes seguirte a ti mismo.")

        self.db.insert(
            sentence="""
                INSERT OR IGNORE INTO Sigue (nombreUsuarioSeguido, nombreUsuarioSeguidor)
                VALUES (?, ?)
            """,
            parameters=[target, viewer]
        )
        return True

    # -------------------------------------------------
    # ✅ dejar de seguir usuario
    # -------------------------------------------------
    def dejar_seguir_usuario(self, viewer: str, target: str) -> bool:
        viewer = (viewer or "").strip()
        target = (target or "").strip()

        if not viewer or not target:
            raise ValueError("Datos inválidos")
        if viewer == target:
            return True

        self.db.delete(
            sentence="""
                DELETE FROM Sigue
                WHERE nombreUsuarioSeguido = ?
                  AND nombreUsuarioSeguidor = ?
            """,
            parameters=[target, viewer]
        )
        return True

    # -------------------------------------------------
    # Caso de uso: Consultar perfil (doc 9.8)
    # -------------------------------------------------
    def consultar_perfil(self, nickname: str, viewer: str = None) -> dict:
        nickname = (nickname or "").strip()
        viewer = (viewer or "").strip() if viewer else None

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

        favoritos = []
        try:
            fav_rows = self.db.select(
                sentence="""
                    SELECT p.nombrePokemon, p.imagen
                    FROM PokemonFavoritos f
                    JOIN PokemonPokedex p ON p.nombrePokemon = f.nombrePokemon
                    WHERE f.nombreUsuario = ?
                    LIMIT 6
                """,
                parameters=[nickname]
            )
            favoritos = [dict(r) for r in fav_rows] if fav_rows else []
        except Exception:
            favoritos = []

        es_mio = (viewer is not None and viewer == nickname)
        le_sigo = (self.le_sigue(viewer, nickname) if viewer else False)

        return {
            "nickname": user_row["nombreUsuario"],
            "foto": user_row.get("foto"),
            "numero_seguidores": int(seguidores),
            "numero_seguidos": int(seguidos),
            "favoritos": favoritos,
            "es_mio": bool(es_mio),
            "le_sigo": bool(le_sigo),
            "viewer": viewer
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

    def comprobar_nickname_repe(self, nickname: str) -> int:
        rows = self.db.select(
            sentence="SELECT COUNT(*) AS cantidad FROM Usuario WHERE nombreUsuario = ?",
            parameters=[nickname]
        )
        if not rows:
            return 0
        return int(rows[0]["cantidad"])

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
    # ✅ helper: escapar para LIKE (evita que % y _ “rompan” el filtro)
    # -------------------------------------------------
    def _escape_like(self, text: str) -> str:
        text = (text or "")
        return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    # -------------------------------------------------
    # ✅ Seguidores con filtro por prefix (q)
    # -------------------------------------------------
    def cargar_seguidores(self, nickname_sesion: str, q: str = None) -> list:
        nickname_sesion = (nickname_sesion or "").strip()
        q = (q or "").strip()

        if not nickname_sesion:
            raise ValueError("Nickname vacío")

        params = [nickname_sesion]
        where_extra = ""

        if q:
            q_esc = self._escape_like(q)
            where_extra = " AND u.nombreUsuario LIKE ? ESCAPE '\\' "
            params.append(q_esc + "%")  # prefix

        rows = self.db.select(
            sentence=f"""
                SELECT
                    u.nombreUsuario AS nombreUsuarioSeguidor,
                    u.foto         AS fotoSeguidor,
                    (SELECT COUNT(*) FROM Sigue s2 WHERE s2.nombreUsuarioSeguido   = u.nombreUsuario) AS numSeguidoresDelSeguidor,
                    (SELECT COUNT(*) FROM Sigue s3 WHERE s3.nombreUsuarioSeguidor = u.nombreUsuario) AS numSeguidosDelSeguidor
                FROM Sigue s
                JOIN Usuario u ON u.nombreUsuario = s.nombreUsuarioSeguidor
                WHERE s.nombreUsuarioSeguido = ?
                {where_extra}
                ORDER BY u.nombreUsuario COLLATE NOCASE
            """,
            parameters=params
        )

        return [dict(r) for r in rows] if rows else []

    # -------------------------------------------------
    # ✅ Seguidos con filtro por prefix (q)
    # -------------------------------------------------
    def cargar_seguidos(self, nickname_sesion: str, q: str = None) -> list:
        nickname_sesion = (nickname_sesion or "").strip()
        q = (q or "").strip()

        if not nickname_sesion:
            raise ValueError("Nickname vacío")

        params = [nickname_sesion]
        where_extra = ""

        if q:
            q_esc = self._escape_like(q)
            where_extra = " AND u.nombreUsuario LIKE ? ESCAPE '\\' "
            params.append(q_esc + "%")  # prefix

        rows = self.db.select(
            sentence=f"""
                SELECT
                    u.nombreUsuario AS nombreUsuarioSeguido,
                    u.foto         AS fotoSeguido,
                    (SELECT COUNT(*) FROM Sigue s2 WHERE s2.nombreUsuarioSeguido   = u.nombreUsuario) AS numSeguidoresDelSeguido,
                    (SELECT COUNT(*) FROM Sigue s3 WHERE s3.nombreUsuarioSeguidor = u.nombreUsuario) AS numSeguidosDelSeguido
                FROM Sigue s
                JOIN Usuario u ON u.nombreUsuario = s.nombreUsuarioSeguido
                WHERE s.nombreUsuarioSeguidor = ?
                {where_extra}
                ORDER BY u.nombreUsuario COLLATE NOCASE
            """,
            parameters=params
        )

        return [dict(r) for r in rows] if rows else []

    # -------------------------------------------------
    # Eliminar seguidor / seguido (igual)
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

    def eliminar_seguido(self, nickname_sesion: str, seguido: str) -> bool:
        nickname_sesion = (nickname_sesion or "").strip()
        seguido = (seguido or "").strip()
        if not nickname_sesion or not seguido:
            raise ValueError("Datos inválidos")

        self.db.delete(
            sentence="""
                DELETE FROM Sigue
                WHERE nombreUsuarioSeguido = ?
                  AND nombreUsuarioSeguidor = ?
            """,
            parameters=[seguido, nickname_sesion]
        )
        return True

    def get_all(self):
        rows = self.db.select(sentence="SELECT * FROM Usuario")
        return [dict(row) for row in rows]
    
    # -------------------------------------------------
    # MOSTRAR NOTIFICACIONES
    # -------------------------------------------------

    def mostrar_Notificaciones(self, nickname,):
        # 1. Recuperamos a quién sigue
        query_followed = "SELECT nombreUsuarioSeguido FROM Sigue WHERE nombreUsuarioSeguidor = ?"
        followed_rows = self.db.select(query_followed, (nickname,))
        usuarios_lista = [row[0] for row in followed_rows]

        # 2. AÑADIMOS AL PROPIO USUARIO para que vea sus notificaciones
        if nickname not in usuarios_lista:
            usuarios_lista.append(nickname)

        if not usuarios_lista:
            return []

        # 3. Consulta
        placeholders = ','.join(['?'] * len(usuarios_lista))
        
        # Filtros
        nombreUsuarioFiltro = request.args.get("usuario")
        filtroFecha = request.args.get("fecha")
        
        query_notif = f"SELECT nombreUsuario, fecha, info_notificacion FROM Notificacion WHERE nombreUsuario IN ({placeholders})"
        params = usuarios_lista

        if nombreUsuarioFiltro:
            query_notif += " AND nombreUsuario = ?"
            params.append(nombreUsuarioFiltro)

        if filtroFecha:
            query_notif += " AND fecha = ?"
            params.append(filtroFecha)
            
        query_notif += " ORDER BY fecha DESC, rowid DESC"

        rows = self.db.select(query_notif, tuple(params))
        columns = ["nombreUsuario", "fecha", "info_notificacion"]
        return [dict(zip(columns, row)) for row in rows]

    def crear_notificacion(self, nickname, mensaje):
        try:
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO Notificacion (nombreUsuario, fecha, info_notificacion) VALUES (?, ?, ?)"
            self.db.insert(sql, [nickname, fecha_actual, mensaje])
            return True
        except Exception as e:
            print(f"Error (Posible duplicado en el mismo segundo): {e}")
            return False

    # -------------------------------------------------
    # -------------------------------------------------

    # admin (tu código igual)
    def obtenerCuentas(self, filtro_nombre=None):
        query = "SELECT nombreUsuario, foto, rol FROM Usuario WHERE rol > 0"
        params = None
        if filtro_nombre:
            query += " AND nombreUsuario LIKE ?"
            params = [f"%{filtro_nombre}%"]

        try:
            rows = self.db.select(query, params)
            users_list = []
            for row in rows:
                rol_numero = row['rol']
                try:
                    rol_numero = int(rol_numero)
                except:
                    rol_numero = 0

                rol_texto = "Entrenador"
                if rol_numero == 2:
                    rol_texto = "Administrador"

                users_list.append({
                    "nombreUsuario": row['nombreUsuario'],
                    "foto": row['foto'] if row['foto'] else 'img/usuario/user1.png',
                    "rol": rol_texto,
                    "rol_num": rol_numero
                })
            return users_list
        except Exception as e:
            print(f"ERROR EN GESTOR USUARIOS (Active): {e}")
            return []

    def obtenerCuentasPendientes(self):
        query = "SELECT nombreUsuario, foto, rol FROM Usuario WHERE rol = 0"
        try:
            rows = self.db.select(query)
            users_list = []
            for row in rows:
                users_list.append({
                    "nombreUsuario": row['nombreUsuario'],
                    "foto": row['foto'] if row['foto'] else 'img/usuario/user1.png',
                    "rol": row['rol']
                })
            return users_list
        except Exception as e:
            print(f"ERROR EN PENDIENTES: {e}")
            return []

    def obtener_id_por_nickname(self, nickname):
        sql = "SELECT id FROM Usuario WHERE nombreUsuario = ?"
        rows = self.db.select(sql, [nickname])
        
        if rows:
            item = rows[0]
            if isinstance(item, dict):
                return item['id']
            return item[0]
        return None

    def borrarCuenta(self, nickname):
        query = "DELETE FROM Usuario WHERE nombreUsuario = ?"
        try:
            self.db.delete(query, (nickname,))
            return True
        except Exception as e:
            print(f"ERROR AL BORRAR CUENTA: {e}")
            return False

    def aprobarCuenta(self, nickname):
        query = "UPDATE Usuario SET rol = 1 WHERE nombreUsuario = ?"
        try:
            self.db.update(query, (nickname,))
            print(f"Usuario {nickname} APROBADO")
            return True
        except Exception as e:
            print(f"ERROR APROBANDO CUENTA: {e}")
            return False

    def update_user_admin(self, antiguo_nick, nuevo_nick, nombre, ape1, ape2, desc):
        query = """
            UPDATE Usuario
            SET nombreUsuario = ?, nombre = ?, apellido1 = ?, apellido2 = ?, descripcion = ?
            WHERE nombreUsuario = ?
        """
        try:
            params = (nuevo_nick, nombre, ape1, ape2, desc, antiguo_nick)
            self.db.update(query, params)
            print(f"Usuario {antiguo_nick} actualizado a {nuevo_nick}")
            return True
        except Exception as e:
            print(f"--- ERROR ACTUALIZANDO USUARIO (ADMIN): {e} ---")
            return False
