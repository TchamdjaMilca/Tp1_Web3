"""
Pour démontrer l'utilisation des templates
"""

import random

from flask import Flask, render_template    
import bd

app = Flask(__name__)


@app.route('/')
def index():
    """Page d'index"""
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT s.id_service,s.titre,s.localisation, c.nom_categorie FROM services s' \
                ' join categories c on s.id_categorie = c.id_categorie WHERE s.actif=1 LIMIT 5')
                service = curseur.fetchall()
                print(service)
        return render_template('index.jinja', service=service)
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return "Erreur de connexion à la base de données"
@app.route('/details')
def details_service():
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT * FROM services s join categories c on s.id_categorie =c.id_categorie')
                service = curseur.fetchone()
        return render_template('details.jinja', service=service)
    except Exception as e:
        return "Erreur de connexion a la bd", 500
@app.route('/ajout')
def ajout_service():
    """Ajouter un service à la base de données"""

    return render_template('ajout.jinja')

@app.route('/liste')
def liste_service():
    """Ajouter un service à la base de données"""

    return render_template('liste.jinja')

if __name__ == '__main__':
    app.run(debug=True)
