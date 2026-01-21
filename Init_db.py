import sqlite3


connection = sqlite3.connect('database.db')

# crée un curseur pour exécuter des commandes SQL
cur = connection.cursor()


cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        statut TEXT DEFAULT 'A faire',
        urgence TEXT DEFAULT 'primary',
        date_echeance TEXT,
        is_recurring BOOLEAN DEFAULT 0
    )
''')
#test
# Ajout d'une tâche de test pour vérifier que ça marche
cur.execute("INSERT INTO tasks (titre, statut, urgence) VALUES (?, ?, ?)",
            ('Finir le projet SQL', 'A faire', 'danger'))

#  Valider les changements et fermer la connexion
connection.commit()
connection.close()

print("La base de données a été initialisée avec succès !")