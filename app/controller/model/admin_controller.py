class AdminController:
    def __init__(self, db):
        self.db = db

    def get_active_users(self, filtro_nombre=None):
        """
        Obtiene todos los usuarios que NO están pendientes.
        Si recibe filtro_nombre, busca por coincidencias (LIKE).
        """
        query = """
            SELECT id, nombreUsuario, foto, rol 
            FROM Usuario 
            WHERE rol > 0
        """
        params = None
        if filtro_nombre:
            query += " AND nombreUsuario LIKE ?"
            params = [f"%{filtro_nombre}%"] # Los % son para buscar texto parcial

        try:
            rows = self.db.select(query, params)
            users_list = []
            for row in rows:
                # TRADUCCIÓN DE NÚMERO A TEXTO PARA LA VISTA
                rol_numero = row['rol']
                try:
                    rol_numero = int(rol_numero)
                except:
                    rol_numero = 0
                rol_texto = "Entrenador"
                if rol_numero == 2:
                    rol_texto = "Administrador"
                
                users_list.append({
                    "id": row['id'], 
                    "nombreUsuario": row['nombreUsuario'],
                    "foto": row['foto'],
                    "rol": rol_texto, # Enviamos el texto "Entrenador" en vez del número 1
                    "rol_num": rol_numero
                })
            
            return users_list

        except Exception as e:
            print(f"ERROR EN MODELO ADMIN: {e}")
            return []

    def get_pending_users(self):
        """
        Obtiene solo los usuarios con estado PENDIENTE.
        """
        query = "SELECT id, nombreUsuario, foto, rol FROM Usuario WHERE rol = 0"
        try:
            rows = self.db.select(query)
            users_list = []
            for row in rows:
                users_list.append({
                    "id": row['id'], 
                    "nombreUsuario": row['nombreUsuario'],
                    "foto": row['foto'],
                    "rol": row['rol']
                })
            return users_list
        except Exception as e:
            print(f"ERROR EN PENDIENTES: {e}")
            return []