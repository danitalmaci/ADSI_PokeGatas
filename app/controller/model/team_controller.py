class TeamController:

    def __init__(self, db):
        self.db = db

    # Necesario para la Figura 4.3.7.1 (Listar equipos antes de borrar)
    def get_teams_by_user(self, user_id):
        # Usamos el nombre real de tu tabla: 'equipos'
        rows = self.db.select(
            sentence="SELECT * FROM equipos WHERE user_id = ?",
            parameters=[user_id]
        )
        return [dict(row) for row in rows]

    # Implementación del Diagrama 9.23: Eliminar Equipo
    # Equivale al método: eliminarEquipo(idEquipo)
    def delete_team(self, team_id):
        if not team_id:
            return False

        try:
            # Paso 4.1 del Diagrama 9.23: DELETE FROM PokemonEquipo...
            # Borramos primero los pokémon asociados para mantener consistencia
            self.db.delete(
                sentence="DELETE FROM PokemonEquipo WHERE equipo_id = ?",
                parameters=[team_id]
            )

            # Paso 4.2 del Diagrama 9.23: DELETE FROM EquipoPokemon...
            # En tu esquema la tabla se llama 'equipos'
            self.db.delete(
                sentence="DELETE FROM equipos WHERE id = ?",
                parameters=[team_id]
            )
            return True
            
        except Exception as e:
            print(f"Error borrando equipo: {e}")
            return False