import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def accueil():
    conn = get_db_connection()
    
    # --- LOGIQUE DE TRI ---
    filtre = request.args.get('trie', 'defaut')
    sql_query = 'SELECT * FROM tasks'
    
    if filtre == 'date_croissante':
        sql_query += ' ORDER BY date_echeance ASC'
    elif filtre == 'date_decroissante':
        sql_query += ' ORDER BY date_echeance DESC'
    elif filtre == 'urgence':
        sql_query += ''' ORDER BY CASE urgence 
                         WHEN 'danger' THEN 1 
                         WHEN 'warning' THEN 2 
                         WHEN 'primary' THEN 3 
                         ELSE 4 END ASC, date_echeance ASC'''
    elif filtre == 'alphabetique':
        sql_query += ' ORDER BY titre ASC'
    else:
        sql_query += ''' ORDER BY CASE urgence 
                         WHEN 'danger' THEN 1 
                         WHEN 'warning' THEN 2 
                         WHEN 'primary' THEN 3 
                         ELSE 4 END ASC, date_echeance ASC'''

    taches = conn.execute(sql_query).fetchall()
    projets_db = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    
    # --- PREPARATION DES DONNEES ---
    liste_projets = []
    for p in projets_db:
        taches_projet = [t for t in taches if t['project_id'] == p['id']]
        total = len(taches_projet)
        fait = len([t for t in taches_projet if t['statut'] == 'Terminée'])
        pourcentage = int((fait / total) * 100) if total > 0 else 0
        liste_projets.append({'infos': p, 'pourcentage': pourcentage, 'taches': taches_projet})

    # Filtres pour les listes principales
    a_faire = [t for t in taches if t['statut'] == 'A faire' and t['project_id'] is None]
    terminees = [t for t in taches if t['statut'] == 'Terminée' and t['project_id'] is None]
    
    today = date.today().isoformat()
    
    # Statistiques
    stat_danger = len([t for t in taches if t['urgence'] == 'danger'])
    stat_warning = len([t for t in taches if t['urgence'] == 'warning'])
    stat_primary = len([t for t in taches if t['urgence'] == 'primary'])

    return render_template("index.html", 
                           a_faire=a_faire, 
                           terminees=terminees, 
                           projets=liste_projets,
                           today=today,
                           stats={'danger': stat_danger, 'warning': stat_warning, 'primary': stat_primary})

# --- ROUTES D'ACTION ---

@app.route('/ajouter', methods=['POST'])
def ajouter_tache():
    # C'EST ICI QUE L'ERREUR SE PRODUISAIT SOUVENT
    # On s'assure de bien utiliser les parenthèses ()
    titre = request.form.get('titre')
    date_echeance = request.form.get('date')
    urgence = request.form.get('urgence')
    
    # Récupération sécurisée de l'ID projet
    projet_id = request.form.get('projet_id')
    
    # Si projet_id est vide ou une chaine vide, on le met à None
    if not projet_id or projet_id.strip() == "":
        projet_id = None

    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (titre, statut, urgence, date_echeance, project_id) VALUES (?, ?, ?, ?, ?)',
                 (titre, 'A faire', urgence, date_echeance, projet_id))
    conn.commit()
    conn.close()
    
    # On redirige simplement vers l'accueil. 
    # Le Javascript (script.js) s'occupera de rouvrir le bon onglet.
    return redirect('/')

@app.route('/modifier/<int:id>', methods=['POST'])
def modifier_tache(id):
    titre = request.form.get('titre')
    date_echeance = request.form.get('date')
    urgence = request.form.get('urgence')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET titre = ?, date_echeance = ?, urgence = ? WHERE id = ?',
                 (titre, date_echeance, urgence, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/ajouter_projet', methods=['POST'])
def ajouter_projet():
    nom = request.form.get('nom_projet')
    conn = get_db_connection()
    conn.execute('INSERT INTO projects (nom) VALUES (?)', (nom,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/valider/<int:id>')
def valider_tache(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET statut = 'Terminée' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    # Cette astuce permet de rester sur la même page sans recharger tout l'historique
    return redirect('/')

@app.route('/invalider/<int:id>')
def invalider_tache(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET statut = 'A faire' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/supprimer/<int:id>')
def supprimer_tache(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)