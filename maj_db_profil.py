import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT NULL")
    cursor.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT 'system'")
    cursor.execute("ALTER TABLE users ADD COLUMN notif_email INTEGER DEFAULT 1")
    cursor.execute("ALTER TABLE users ADD COLUMN notif_push INTEGER DEFAULT 1")
    print("✅ Base de données mise à jour avec succès (Nouvelles colonnes ajoutées) !")
except sqlite3.OperationalError as e:
    print(f"Information : {e} (Les colonnes existent peut-être déjà).")

conn.commit()
conn.close()