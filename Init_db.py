import sqlite3

# 1. Connexion à la base de données (elle sera créée si elle n'existe pas)
connection = sqlite3.connect('database.db')

# 2. On crée un curseur pour exécuter des commandes SQL
cur = connection.cursor()

# 3. Création de la table 'tasks' (Taches)
# J'ai repris les champs de ton code actuel (titre, statut, urgence)
# et ajouté ceux demandés par le cahier des charges (date, recurrence, etc.)
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
# 4. (Optionnel) Ajouter une tâche de test pour vérifier que ça marche
cur.execute("INSERT INTO tasks (titre, statut, urgence) VALUES (?, ?, ?)",
            ('Finir le projet SQL', 'A faire', 'danger'))

# 5. Valider les changements et fermer la connexion
connection.commit()
connection.close()

print("La base de données a été initialisée avec succès !")