from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    # Cette ligne permet d'accéder aux colonnes par leur nom (ex: tache['titre'])
    conn.row_factory = sqlite3.Row 
    return conn

@app.route("/")
def accueil():
    conn = get_db_connection()
    # On récupère toutes les tâches de la base de données
    taches = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template("index.html", taches=taches)


@app.route('/ajouter', methods=['POST'])
def ajouter_tache():

    titre_recu = request.form.get('titre')
    
    # On insère la nouvelle tâche dans la BDD
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (titre, statut, urgence) VALUES (?, ?, ?)',
                 (titre_recu, 'A faire', 'primary'))
    conn.commit()
    conn.close()
  

    return redirect('/')







if __name__ == "__main__":
    app.run(debug=True)