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
    
    def borrarCuenta(self, nickname):
        """
        Elimina la cuenta de un usuario dado su nickname.
        """
        query = "DELETE FROM Usuario WHERE nombreUsuario = ?"
        try:
            self.db.delete(query, (nickname,))
            return True
        except Exception as e:
            print(f"ERROR AL BORRAR CUENTA: {e}")
            return False
        
    def aprobarCuenta(self, nickname):
        """
        Aprueba la cuenta de un usuario dado su nickname.
        """
        query = "UPDATE Usuario SET rol = 1 WHERE nombreUsuario = ?"
        try:
            self.db.update(query, (nickname,))
            print(f"Usuario {nickname} APROBADO")
            return True
        except Exception as e:
            print(f"ERROR APROBANDO CUENTA: {e}")
            return False
        
    def get_user_by_nickname(self, nickname):
        """Obtiene todos los datos de un usuario dado su nickname."""
        query = "SELECT * FROM Usuario WHERE nombreUsuario = ?"
        try:
            rows = self.db.select(query, (nickname,))
            if rows:
                row = rows[0]
                # convertir a diccionario CON LAS CLAVES QUE USA EL HTML
                return {
                    "id": row['id'],
                    # IMPORTANTE: El HTML espera 'nickname', no 'nombreUsuario'
                    "nickname": row['nombreUsuario'], 
                    "nombre": row['nombre'],
                    # IMPORTANTE: El HTML espera 'ape1', no 'apellido1'
                    "ape1": row['apellido1'],
                    # IMPORTANTE: El HTML espera 'ape2', no 'apellido2'
                    "ape2": row['apellido2'],
                    "descripcion": row['descripcion'],
                    "foto": row['foto'],
                    "rol": row['rol']
                }
            return None
        except Exception as e:
            print(f"Error recuperando usuario {nickname}: {e}")
            return None
        
    def get_user_by_nickname(self, nickname):
        """Obtiene todos los datos de un usuario dado su nickname."""
        query = "SELECT * FROM Usuario WHERE nombreUsuario = ?"
        try:
            rows = self.db.select(query, (nickname,))
            if rows:
                row = rows[0]
                # --- CAMBIO IMPORTANTE AQUI ---
                # Estamos mapeando los nombres de la base de datos (derecha)
                # a los nombres que usa tu HTML (izquierda)
                return {
                    "id": row['id'],
                    "nickname": row['nombreUsuario'], # HTML pide 'nickname'
                    "nombre": row['nombre'],
                    "ape1": row['apellido1'],         # HTML pide 'ape1'
                    "ape2": row['apellido2'],         # HTML pide 'ape2'
                    "descripcion": row['descripcion'],
                    "foto": row['foto'],
                    "rol": row['rol']
                }
            return None
        except Exception as e:
            print(f"Error recuperando usuario {nickname}: {e}")
            return None
        
    def update_user(self, antiguo_nick, nuevo_nick, nombre, ape1, ape2, desc):
        """
        Modifica los datos de un usuario en la base de datos.
        """
        query = """
            UPDATE Usuario 
            SET nombreUsuario = ?, nombre = ?, apellido1 = ?, apellido2 = ?, descripcion = ?
            WHERE nombreUsuario = ?
        """
        try:
            params = (nuevo_nick, nombre, ape1, ape2, desc, antiguo_nick)
            self.db.update(query, params)
            
            print(f"Usuario {antiguo_nick} actualizado. a {nuevo_nick}")
            return True
        except Exception as e:
            print(f"--- ERROR ACTUALIZANDO USUARIO: {e} ---")
            return False