"""
Pour démontrer l'utilisation des templates
"""

import random

from flask import Flask, render_template, request , abort    
import re
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
  


@app.route('/ajout', methods=['GET', 'POST'])
def ajouter_service():
    """Ajout d'un nouveau service avec validation"""
 
    caracteres_interdits = re.compile('<|>')
    format_image = re.compile(r'^[\w,\s-]+\.(jpg|jpeg|png|gif)$', re.IGNORECASE)
    class_titre = ''
    class_localisation = ''
    class_description = ''
    class_cout = ''
    class_categorie = ''
    class_nom_photo = ''
 
    titre = ''
    localisation = ''
    description = ''
    cout = ''
    statut = ''
    categorie = ''
    nom_photo= ''
 
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute("SELECT id_categorie, nom_categorie FROM categories")
                categories = curseur.fetchall()
 
                if request.method == 'POST':
                    titre = request.form.get('titre', '').strip()
                    localisation = request.form.get('localisation', '').strip()
                    description = request.form.get('description', '').strip()
                    cout = request.form.get('cout', '').strip()
                    statut = 1 if request.form.get('statut') == '1' else 0
                    categorie = request.form.get('categorie', '').strip()
                    nom_photo = request.form.get('photo', '').strip()
 
                    if not titre or caracteres_interdits.search(titre):
                        class_titre = 'is-invalid'
                    if not localisation :
                        class_localisation = 'is-invalid'
                    if not description or caracteres_interdits.search(description):
                        class_description = 'is-invalid'
                    
                    if not cout or float(cout) < 0:
                        class_cout = 'is-invalid'
                    if not categorie or not any(str(cat['id_categorie']) == categorie for cat in categories):
                        class_categorie = 'is-invalid'
                    if not nom_photo or not format_image.search(nom_photo):
                        class_nom_photo = 'is-invalid'
                    if not (class_titre or class_localisation or class_description or class_cout  or class_categorie or class_nom_photo):
                        curseur.execute("""
                            INSERT INTO services (titre, localisation, description, cout, actif,photo, id_categorie)
                            VALUES (%(titre)s, %(localisation)s, %(description)s, %(cout)s, %(statut)s,%(nom_photo)s ,%(categorie)s)
                        """, {
                            'titre': titre,
                            'localisation': localisation,
                            'description': description,
                            'cout': cout,
                            'statut': statut,
                            'nom_photo': nom_photo,
                            'categorie': categorie
                        })
                        
                        return render_template('index.jinja', message="Service ajouté avec succès!", services=[])
 
        return render_template(
            'ajout.jinja',
            categories=categories,
            titre=titre,
            localisation=localisation,
            description=description,
            cout=cout,
            statut=statut,
            nom_photo=nom_photo,
            categorie=categorie,
            class_titre=class_titre,
            class_localisation=class_localisation,
            class_description=class_description,
            class_cout=class_cout,
            class_nom_photo=class_nom_photo,
            class_categorie=class_categorie
        )
    except Exception as e:
        print(f"Erreur lors de l'ajout du service : {e}")
        return render_template('ajout.jinja', categories=[], titre=titre, localisation=localisation, description=description, cout=cout, statut=statut, nom_photo=nom_photo,categorie=categorie), 500






@app.route('/liste')
def liste_service():
    """Aficher les services de la base de données"""
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
