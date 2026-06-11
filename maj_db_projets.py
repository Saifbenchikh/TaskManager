import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE projects ADD COLUMN date_limite TEXT DEFAULT NULL")
    cursor.execute("ALTER TABLE projects ADD COLUMN statut TEXT DEFAULT 'Actif'")
    print("✅ Base de données mise à jour avec succès (Dates et Archivage ajoutés) !")
except sqlite3.OperationalError as e:
    print(f"Information : {e} (Les colonnes existent peut-être déjà).")

conn.commit()
conn.close()