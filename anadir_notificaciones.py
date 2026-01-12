# archivo: anadir_notificaciones.py

from app.database.connection import Connection
from datetime import date

def anadir_notificaciones():
    db = Connection()

    # -----------------------------
    # 1️⃣ Añadir relaciones "Sigue"
    # -----------------------------
    sigue_data = [
        ("ash_ketchum", "gary_oak"),
        ("ash_ketchum", "admin_jefe"),
        ("gary_oak", "ash_ketchum"),
        ("admin_jefe", "gary_oak"),
        ("admin_jefe", "ash_ketchum"),
        ("gary_oak", "admin_jefe"),
    ]

    print("Añadiendo relaciones Sigue...")
    for seguidor, seguido in sigue_data:
        try:
            db.insert(
                "INSERT OR IGNORE INTO Sigue (nombreUsuarioSeguidor, nombreUsuarioSeguido) VALUES (?, ?)",
                (seguidor, seguido)
            )
            print(f"  {seguidor} sigue a {seguido}")
        except Exception as e:
            print(f"Error añadiendo {seguidor} sigue a {seguido}: {e}")

    # -----------------------------
    # 2️⃣ Añadir Notificaciones
    # -----------------------------
    notif_data = [
        ("gary_oak", date(2026, 1, 12), "Le dio like a tu foto"),
        ("admin_jefe", date(2026, 1, 12), "Comentó tu publicación"),
        ("ash_ketchum", date(2026, 1, 11), "Te ha enviado un regalo"),
        ("gary_oak", date(2026, 1, 10), "Te mencionó en un post"),
        ("admin_jefe", date(2026, 2, 12), "Comentó tu publicación"),
        ("ash_ketchum", date(2026, 2, 11), "Te ha enviado un regalo"),
        ("gary_oak", date(2026, 2, 10), "Te mencionó en un post"),
    ]

    print("Añadiendo notificaciones...")
    for usuario, fecha, info in notif_data:
        try:
            db.insert(
                "INSERT OR IGNORE INTO Notificacion (nombreUsuario, fecha, info_notificacion) VALUES (?, ?, ?)",
                (usuario, fecha, info)
            )
            print(f"  Notificación para {usuario} el {fecha}: {info}")
        except Exception as e:
            print(f"Error añadiendo notificación para {usuario}: {e}")

    print("¡Datos de ejemplo añadidos correctamente!")

if __name__ == "__main__":
    anadir_notificaciones()
