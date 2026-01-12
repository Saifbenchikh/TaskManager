import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def accueil():
    conn = get_db_connection()
    taches = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    
    # On sépare les tâches en deux listes pour les onglets
    a_faire = [t for t in taches if t['statut'] == 'A faire']
    terminees = [t for t in taches if t['statut'] == 'Terminée']
    
    return render_template("index.html", a_faire=a_faire, terminees=terminees)

@app.route('/ajouter', methods=['POST'])
def ajouter_tache():
    titre = request.form.get('titre')
    date = request.form.get('date')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (titre, statut, urgence, date_echeance) VALUES (?, ?, ?, ?)',
                 (titre, 'A faire', 'primary', date))
    conn.commit()
    conn.close()
    return redirect('/')

# --- NOUVELLES ROUTES ---

# 1. Valider une tâche (La passer dans l'onglet "Terminée")
@app.route('/valider/<int:id>')
def valider_tache(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET statut = 'Terminée', urgence = 'success' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# 2. Supprimer une tâche
@app.route('/supprimer/<int:id>')
def supprimer_tache(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# 3. Modifier une tâche (Renommer ou changer date)
@app.route('/modifier/<int:id>', methods=['POST'])
def modifier_tache(id):
    nouveau_titre = request.form.get('titre')
    nouvelle_date = request.form.get('date')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET titre = ?, date_echeance = ? WHERE id = ?',
                 (nouveau_titre, nouvelle_date, id))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)