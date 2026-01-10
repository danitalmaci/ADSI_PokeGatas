class AdminController:
    def __init__(self, db):
        self.db = db

    def get_active_users(self):
        """
        Obtiene todos los usuarios que NO están pendientes.
        Usa el método .select() de tu clase Connection.
        """
        query = """
            SELECT id, nombreUsuario, foto, rol, estado 
            FROM Usuario 
            WHERE estado != 'PENDIENTE'
        """
        
        try:
            rows = self.db.select(query)
            users_list = []
            for row in rows:
                users_list.append({
                    "id": row['id'], 
                    "nombreUsuario": row['nombreUsuario'],
                    "foto": row['foto'],
                    "rol": row['rol'],
                    "estado": row['estado']
                })
            
            return users_list

        except Exception as e:
            print(f"ERROR EN MODELO ADMIN: {e}")
            return []

    def get_pending_users(self):
        """
        Obtiene solo los usuarios con estado PENDIENTE.
        """
        query = "SELECT id, nombreUsuario, foto, rol, estado FROM Usuario WHERE estado = 'PENDIENTE'"
        try:
            rows = self.db.select(query)
            users_list = []
            for row in rows:
                users_list.append({
                    "id": row['id'], 
                    "nombreUsuario": row['nombreUsuario'],
                    "foto": row['foto'],
                    "rol": row['rol'],
                    "estado": row['estado']
                })
            return users_list
        except Exception as e:
            print(f"ERROR EN PENDIENTES: {e}")
            return []