from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# --- DONNÉES PROVISOIRES (En attendant la Base de Données de Martin) ---
# On simule une liste de tâches pour que le site ne soit pas vide
mes_taches = [
    {'titre': 'Apprendre le Python', 'statut': 'En cours', 'urgence': 'primary'},
    {'titre': 'Créer le formulaire HTML', 'statut': 'En cours', 'urgence': 'warning'},
    {'titre': 'Connecter la base de données', 'statut': 'A faire', 'urgence': 'danger'}
]

# --- ROUTE 1 : La Page d'Accueil (Ce qu'on voit) ---
@app.route("/")
def accueil():
    # On envoie la liste "mes_taches" à la page HTML
    return render_template("index.html", taches=mes_taches)

# --- ROUTE 2 : La Réception du Formulaire (La partie invisible) ---
@app.route('/ajouter', methods=['POST'])
def ajouter_tache():
    # 1. On récupère ce que Nino a envoyé depuis le champ nommé "titre"
    TaskManager = request.form.get('titre')
    
    # 2. LE TEST : On l'affiche dans ton terminal (la fenêtre noire)
    print("----------------------------------------------------")
    print("NOUVELLE TACHE REÇUE : " + str(TaskManager))
    print("----------------------------------------------------")
    
    # 3. On redirige l'utilisateur vers l'accueil pour ne pas bloquer
    return redirect('/')

# --- Lancement du Serveur ---
if __name__ == "__main__":
    app.run(debug=True)