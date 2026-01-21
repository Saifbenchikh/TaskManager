import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

#nettoie les anciennes tables pour éviter les conflits
cursor.execute("DROP TABLE IF EXISTS tasks")
cursor.execute("DROP TABLE IF EXISTS projects")

# Creation de la table PROJETS 
cursor.execute('''
    CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT
    )
''')

# Creation de la table TACHES avec le lien vers les projets
cursor.execute('''
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        statut TEXT DEFAULT 'A faire',
        urgence TEXT DEFAULT 'primary',
        date_echeance TEXT,
        project_id INTEGER,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
''')

# exmple
cursor.execute("INSERT INTO projects (nom) VALUES (?)", ("Mon Premier Projet",))
cursor.execute("INSERT INTO tasks (titre, statut, urgence, project_id) VALUES (?, ?, ?, ?)", ("Tester le site", "A faire", "danger", 1))

connection.commit()
connection.close()
print("✅ Base de données mise à jour avec succès !")