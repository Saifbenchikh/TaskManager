from flask import Flask, render_template, request, redirect

app = Flask(__name__)

mes_taches = [

]


@app.route("/")
def accueil():

    return render_template("index.html", taches=mes_taches)


@app.route('/ajouter', methods=['POST'])
def ajouter_tache():

    titre_recu = request.form.get('titre')
    
    nouvelle_tache = {
        'titre': titre_recu,
        'statut': 'A faire',
        'urgence': 'primary' 
    }
    

    mes_taches.append(nouvelle_tache)
    

    return redirect('/')







if __name__ == "__main__":
    app.run(debug=True)