import os
import sqlite3
import json
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import date

app = Flask(__name__)
app.secret_key = 'super_cle_secrete_a_changer_en_production'

# --- CONFIGURATION UPLOAD AVATARS ---
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'avatars')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('accueil'))
        else:
            flash('Identifiants incorrects.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ROUTE GESTION DE COMPTE / PROFIL ---
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'general':
            username = request.form.get('username')
            email = request.form.get('email')
            try:
                conn.execute('UPDATE users SET username = ?, email = ? WHERE id = ?', (username, email, user_id))
                conn.commit()
                session['username'] = username
                flash('Informations générales mises à jour !', 'success')
            except sqlite3.IntegrityError:
                flash('Erreur : Cet email ou pseudo est déjà pris.', 'danger')

        elif action == 'security':
            new_password = request.form.get('password')
            if new_password:
                hash_pwd = generate_password_hash(new_password)
                conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hash_pwd, user_id))
                conn.commit()
                flash('Mot de passe mis à jour avec succès !', 'success')
                
        elif action == 'prefs':
            theme = request.form.get('theme', 'system')
            notif_email = 1 if request.form.get('notif_email') else 0
            notif_push = 1 if request.form.get('notif_push') else 0
            conn.execute('UPDATE users SET theme = ?, notif_email = ?, notif_push = ? WHERE id = ?', 
                         (theme, notif_email, notif_push, user_id))
            conn.commit()
            flash('Préférences sauvegardées !', 'success')

        elif action == 'avatar':
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename != '' and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(f"user_{user_id}.{ext}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    conn.execute('UPDATE users SET avatar = ? WHERE id = ?', (filename, user_id))
                    conn.commit()
                    flash('Photo de profil mise à jour !', 'success')
                else:
                    flash('Format non supporté. Utilisez PNG, JPG ou GIF.', 'danger')
        
        conn.close()
        return redirect(url_for('profile'))
        
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return render_template('profile.html', user=user, username=session.get('username'))

# --- API CALENDRIER ---
@app.route('/api/tasks')
@login_required
def api_get_tasks():
    conn = get_db_connection()
    user_id = session['user_id']
    taches = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    events = []
    for t in taches:
        if t['statut'] != 'Terminée' and t['date_echeance']:
            color = '#4F46E5' # primary
            if t['urgence'] == 'danger': color = '#EF4444' # Rouge
            if t['urgence'] == 'warning': color = '#F59E0B' # Orange
            
            events.append({
                'id': t['id'],
                'title': t['titre'],
                'start': t['date_echeance'],
                'backgroundColor': color,
                'borderColor': color
            })
    return jsonify(events)

# --- ROUTES DE L'APPLICATION ---
@app.route("/")
@login_required
def accueil():
    conn = get_db_connection()
    user_id = session['user_id']
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
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
    
    # --- GESTION DES PROJETS ---
    projets_actifs_db = conn.execute('SELECT * FROM projects WHERE user_id = ? AND (statut = "Actif" OR statut IS NULL)', (user_id,)).fetchall()
    projets_archives_db = conn.execute('SELECT * FROM projects WHERE user_id = ? AND statut = "Archivé"', (user_id,)).fetchall()
    conn.close()
    
    def formater_projets(liste_db):
        resultat = []
        for p in liste_db:
            taches_projet = [t for t in taches if t['project_id'] == p['id']]
            total = len(taches_projet)
            fait = len([t for t in taches_projet if t['statut'] == 'Terminée'])
            pourcentage = int((fait / total) * 100) if total > 0 else 0
            resultat.append({'infos': p, 'pourcentage': pourcentage, 'taches': taches_projet})
        return resultat

    liste_projets = formater_projets(projets_actifs_db)
    liste_projets_archives = formater_projets(projets_archives_db)

    a_faire = [t for t in taches if t['statut'] == 'A faire' and t['project_id'] is None]
    terminees = [t for t in taches if t['statut'] == 'Terminée' and t['project_id'] is None]
    
    today = date.today().isoformat()
    stat_danger = len([t for t in taches if t['urgence'] == 'danger'])
    stat_warning = len([t for t in taches if t['urgence'] == 'warning'])
    stat_primary = len([t for t in taches if t['urgence'] == 'primary'])

    total_taches = len(taches)
    total_terminees = len([t for t in taches if t['statut'] == 'Terminée'])
    taux_completion = int((total_terminees / total_taches) * 100) if total_taches > 0 else 0

    stats_kpi = {
        'total_taches': total_taches,
        'terminees': total_terminees,
        'taux_completion': taux_completion,
        'projets_actifs': len(liste_projets)
    }

    radar_labels = [p['infos']['nom'] for p in liste_projets]
    radar_data = [len(p['taches']) for p in liste_projets]

    dates_taches = {}
    for t in taches:
        if t['date_echeance'] and t['statut'] == 'A faire':
            # On coupe l'heure pour ne garder que la date (YYYY-MM-DD) pour le graphique
            date_str = t['date_echeance'][:10] 
            dates_taches[date_str] = dates_taches.get(date_str, 0) + 1
    
    dates_triees = sorted(dates_taches.keys())
    line_labels = dates_triees[:7]
    line_data = [dates_taches[d] for d in line_labels]

    return render_template("index.html", 
                           a_faire=a_faire, terminees=terminees, 
                           projets=liste_projets, projets_archives=liste_projets_archives, today=today,
                           stats={'danger': stat_danger, 'warning': stat_warning, 'primary': stat_primary},
                           stats_kpi=stats_kpi, radar_labels=json.dumps(radar_labels), radar_data=json.dumps(radar_data),
                           line_labels=json.dumps(line_labels), line_data=json.dumps(line_data),
                           username=session.get('username'), user=user)

# --- ROUTES D'ACTIONS (Ajout, Modif, Suppr) ---
@app.route('/ajouter', methods=['POST'])
@login_required
def ajouter_tache():
    titre = request.form.get('titre')
    date_echeance = request.form.get('date') # Ce sera maintenant au format 'YYYY-MM-DDTHH:MM'
    urgence = request.form.get('urgence')
    projet_id = request.form.get('projet_id') or None
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (titre, statut, urgence, date_echeance, project_id, user_id) VALUES (?, ?, ?, ?, ?, ?)',
                 (titre, 'A faire', urgence, date_echeance, projet_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/modifier/<int:id>', methods=['POST'])
@login_required
def modifier_tache(id):
    titre = request.form.get('titre')
    date_echeance = request.form.get('date')
    urgence = request.form.get('urgence')
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET titre = ?, date_echeance = ?, urgence = ? WHERE id = ? AND user_id = ?',
                 (titre, date_echeance, urgence, id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/ajouter_projet', methods=['POST'])
@login_required
def ajouter_projet():
    nom = request.form.get('nom_projet')
    date_limite = request.form.get('date_limite') or None
    conn = get_db_connection()
    conn.execute('INSERT INTO projects (nom, date_limite, statut, user_id) VALUES (?, ?, ?, ?)', (nom, date_limite, 'Actif', session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/modifier_projet/<int:id>', methods=['POST'])
@login_required
def modifier_projet(id):
    nom = request.form.get('nom_projet')
    date_limite = request.form.get('date_limite') or None
    conn = get_db_connection()
    conn.execute('UPDATE projects SET nom = ?, date_limite = ? WHERE id = ? AND user_id = ?', (nom, date_limite, id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/archiver_projet/<int:id>')
@login_required
def archiver_projet(id):
    conn = get_db_connection()
    conn.execute("UPDATE projects SET statut = 'Archivé' WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/desarchiver_projet/<int:id>')
@login_required
def desarchiver_projet(id):
    conn = get_db_connection()
    conn.execute("UPDATE projects SET statut = 'Actif' WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/supprimer_projet/<int:id>')
@login_required
def supprimer_projet(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE project_id = ? AND user_id = ?', (id, session['user_id']))
    conn.execute('DELETE FROM projects WHERE id = ? AND user_id = ?', (id, session['user_id']))
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

# --- ROUTE CHATBOT API ---
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    user_message = data.get('message', '').lower().strip()
    user_id = session['user_id']
    username = session.get('username', 'Utilisateur')

    if user_message in ['bonjour', 'salut', 'hello', 'coucou']:
        return jsonify({'reply': f"Bonjour {username} ! Comment puis-je vous aider aujourd'hui ?"})

    if 'résumé' in user_message or 'resume' in user_message or 'bilan' in user_message:
        conn = get_db_connection()
        urgent_count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND urgence = 'danger' AND statut = 'A faire'", 
            (user_id,)
        ).fetchone()[0]
        conn.close()
        if urgent_count > 0:
            return jsonify({'reply': f"Vous avez actuellement {urgent_count} tâche(s) urgente(s) en attente. Ne relâchez pas vos efforts !"})
        else:
            return jsonify({'reply': "Excellente nouvelle, vous n'avez aucune tâche urgente en attente !"})

    if 'ajouter' in user_message and ('tâche' in user_message or 'tache' in user_message):
        clean_msg = re.sub(r'ajouter\s+(une\s+)?t[aâ]che\s+', '', user_message, flags=re.IGNORECASE)
        urgence = 'primary'
        if 'urgent' in clean_msg:
            urgence = 'danger'
            clean_msg = clean_msg.replace('urgent', '').strip()
        elif 'important' in clean_msg:
            urgence = 'warning'
            clean_msg = clean_msg.replace('important', '').strip()

        if clean_msg:
            titre = clean_msg.capitalize()
            conn = get_db_connection()
            conn.execute('INSERT INTO tasks (titre, statut, urgence, user_id) VALUES (?, ?, ?, ?)', (titre, 'A faire', urgence, user_id))
            conn.commit()
            conn.close()
            return jsonify({'reply': f'Tâche ajoutée avec succès : "{titre}". Rechargez la page pour la voir apparaître !', 'action': 'reload'})
        else:
            return jsonify({'reply': 'Veuillez préciser le nom de la tâche. Exemple : "Ajouter tâche faire les courses urgent".'})

    return jsonify({'reply': "Désolé, je ne suis pas sûr de comprendre. Essayez de dire 'bonjour', 'résumé', ou 'ajouter tâche [nom de la tâche] urgent'."})

if __name__ == "__main__":
    app.run(debug=True)