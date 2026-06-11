import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Nettoyage des anciennes tables
cursor.execute("DROP TABLE IF EXISTS tasks")
cursor.execute("DROP TABLE IF EXISTS projects")
cursor.execute("DROP TABLE IF EXISTS users")

# Création de la table USERS (incluant avatar, theme, et notifications)
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        avatar TEXT DEFAULT NULL,
        theme TEXT DEFAULT 'system',
        notif_email INTEGER DEFAULT 1,
        notif_push INTEGER DEFAULT 1
    )
''')

# Création de la table PROJETS (liée à un user)
cursor.execute('''
    CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        description TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

# Création de la table TACHES (liée à un projet et à un user)
cursor.execute('''
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        statut TEXT DEFAULT 'A faire',
        urgence TEXT DEFAULT 'primary',
        date_echeance TEXT,
        project_id INTEGER,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

connection.commit()
connection.close()
print("✅ Base de données initialisée avec TOUTES les colonnes (avatar, theme, notifs) !")