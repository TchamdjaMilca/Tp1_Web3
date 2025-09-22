"""
Pour démontrer l'utilisation des templates
"""

import random

from flask import Flask, render_template, request , abort    
import bd

app = Flask(__name__)


@app.route('/')
def index():
    """Page d'index"""
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT s.id_service,s.titre,s.localisation, c.nom_categorie FROM services s' \
                ' join categories c on s.id_categorie = c.id_categorie WHERE s.actif=1 ORDER BY s.date_creation DESC LIMIT 5')
                services = curseur.fetchall()
              
        return render_template('index.jinja', services=services)
    except Exception as e:
        print(e)
        return "Erreur de connexion à la base de données",500
    
@app.route('/details')
def details_service():
    """Détails d'un service"""
    identifiant = request.args.get('id', type =int)
    if not identifiant:
        abort(400,"Identifiant manquant") 
    service={}
    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute('SELECT s.id_service, s.titre, s.description ,s.localisation,s.date_creation, s.actif,s.cout, s.photo, c.nom_categorie as categorie FROM services s ' \
            'join categories c on s.id_categorie =c.id_categorie WHERE s.id_service=%(id)s', {'id': identifiant})
            service = curseur.fetchone()
            if not service:
             abort(404,"Service non trouvé") 
    return render_template('details.jinja', service=service)
  
@app.route('/ajout')
def ajout_service():
    """Ajouter un service à la base de données"""

    return render_template('ajout.jinja')

@app.route('/liste')
def liste_service():
    """Ajouter un service à la base de données"""
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT s.id_service,s.titre,s.localisation, c.nom_categorie FROM services s' \
                ' join categories c on s.id_categorie = c.id_categorie ORDER BY s.date_creation DESC ')
                services = curseur.fetchall()  
        return render_template('liste.jinja', services=services)
    except Exception as e:
        print(e)    
        return "Erreur de connexion à la base de données",500


if __name__ == '__main__':
    app.run(debug=True)
