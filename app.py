from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def accueil():
    # --- C'est ici que Personne C gère les données (pour l'instant) ---
    liste_taches = [
        {'titre': 'Apprendre le Python', 'statut': 'En cours'},
        {'titre': 'Créer notre première page web', 'statut': 'Fait'},
        {'titre': 'Manger une pizza', 'statut': 'A faire'}
    ]
    # ------------------------------------------------------------------

    # On envoie la liste à la page web de Personne B
    return render_template("index.html", taches=liste_taches)

if __name__ == "__main__":
    app.run(debug=True)