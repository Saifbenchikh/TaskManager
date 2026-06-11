import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date

app = Flask(__name__)
# Clé secrète nécessaire pour utiliser les sessions Flask en toute sécurité
app.secret_key = 'super_cle_secrete_a_changer_en_production'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- DÉCORATEUR D'AUTHENTIFICATION ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES D'AUTHENTIFICATION ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hachage du mot de passe
        hash_pwd = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                         (username, email, hash_pwd))
            conn.commit()
            flash('Compte créé avec succès ! Connectez-vous.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Erreur : Ce nom d\'utilisateur ou cet email est déjà pris.', 'danger')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        # Vérification du mot de passe haché
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('accueil'))
        else:
            flash('Identifiants incorrects.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Vide la session
    return redirect(url_for('login'))

# --- ROUTES DE L'APPLICATION (SÉCURISÉES) ---
@app.route("/")
@login_required
def accueil():
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Sécurisation : On filtre UNIQUEMENT les tâches de l'utilisateur
    filtre = request.args.get('trie', 'defaut')
    sql_query = 'SELECT * FROM tasks WHERE user_id = ?'
    
    if filtre == 'date_croissante':
        sql_query += ' ORDER BY date_echeance ASC'
    elif filtre == 'date_decroissante':
        sql_query += ' ORDER BY date_echeance DESC'
    elif filtre == 'urgence':
        sql_query += " ORDER BY CASE urgence WHEN 'danger' THEN 1 WHEN 'warning' THEN 2 WHEN 'primary' THEN 3 ELSE 4 END ASC, date_echeance ASC"
    elif filtre == 'alphabetique':
        sql_query += ' ORDER BY titre ASC'
    else:
        sql_query += " ORDER BY CASE urgence WHEN 'danger' THEN 1 WHEN 'warning' THEN 2 WHEN 'primary' THEN 3 ELSE 4 END ASC, date_echeance ASC"

    taches = conn.execute(sql_query, (user_id,)).fetchall()
    projets_db = conn.execute('SELECT * FROM projects WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    liste_projets = []
    for p in projets_db:
        taches_projet = [t for t in taches if t['project_id'] == p['id']]
        total = len(taches_projet)
        fait = len([t for t in taches_projet if t['statut'] == 'Terminée'])
        pourcentage = int((fait / total) * 100) if total > 0 else 0
        liste_projets.append({'infos': p, 'pourcentage': pourcentage, 'taches': taches_projet})

    a_faire = [t for t in taches if t['statut'] == 'A faire' and t['project_id'] is None]
    terminees = [t for t in taches if t['statut'] == 'Terminée' and t['project_id'] is None]
    
    today = date.today().isoformat()
    stat_danger = len([t for t in taches if t['urgence'] == 'danger'])
    stat_warning = len([t for t in taches if t['urgence'] == 'warning'])
    stat_primary = len([t for t in taches if t['urgence'] == 'primary'])

    return render_template("index.html", 
                           a_faire=a_faire, terminees=terminees, 
                           projets=liste_projets, today=today,
                           stats={'danger': stat_danger, 'warning': stat_warning, 'primary': stat_primary},
                           username=session.get('username')) # On passe le nom d'utilisateur

@app.route('/ajouter', methods=['POST'])
@login_required
def ajouter_tache():
    titre = request.form.get('titre')
    date_echeance = request.form.get('date')
    urgence = request.form.get('urgence')
    projet_id = request.form.get('projet_id') or None
    user_id = session['user_id']

    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (titre, statut, urgence, date_echeance, project_id, user_id) VALUES (?, ?, ?, ?, ?, ?)',
                 (titre, 'A faire', urgence, date_echeance, projet_id, user_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/modifier/<int:id>', methods=['POST'])
@login_required
def modifier_tache(id):
    titre = request.form.get('titre')
    date_echeance = request.form.get('date')
    urgence = request.form.get('urgence')
    user_id = session['user_id']
    
    conn = get_db_connection()
    # Sécurisation : On vérifie que la tâche appartient bien au user (IDOR prevention)
    conn.execute('UPDATE tasks SET titre = ?, date_echeance = ?, urgence = ? WHERE id = ? AND user_id = ?',
                 (titre, date_echeance, urgence, id, user_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/ajouter_projet', methods=['POST'])
@login_required
def ajouter_projet():
    nom = request.form.get('nom_projet')
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute('INSERT INTO projects (nom, user_id) VALUES (?, ?)', (nom, user_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/valider/<int:id>')
@login_required
def valider_tache(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET statut = 'Terminée' WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/invalider/<int:id>')
@login_required
def invalider_tache(id):
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET statut = 'A faire' WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/supprimer/<int:id>')
@login_required
def supprimer_tache(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)