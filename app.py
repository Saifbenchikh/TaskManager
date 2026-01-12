import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permet d'appeler les colonnes par leur nom
    return conn

@app.route("/")
def accueil():
    conn = get_db_connection()
    # On récupère tout depuis la table 'tasks' (nom choisi par Martin)
    taches = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template("index.html", taches=taches)

@app.route('/ajouter', methods=['POST'])
def ajouter_tache():
    # 1. Récupération des données du formulaire HTML
    titre_recu = request.form.get('titre')
    date_recue = request.form.get('date') # On récupère la date choisie

    # 2. Enregistrement dans la Base de Données
    conn = get_db_connection()
    
    # On insère le titre ET la date_echeance
    conn.execute('INSERT INTO tasks (titre, statut, urgence, date_echeance) VALUES (?, ?, ?, ?)',
                 (titre_recu, 'A faire', 'primary', date_recue))
                 
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)