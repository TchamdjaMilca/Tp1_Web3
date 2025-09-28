"""
Pour démontrer l'utilisation des templates
"""

import random

from flask import Flask, render_template, request , abort  , redirect , make_response  
import re
import bd
from flask_babel import Babel,numbers, dates
from flask.logging import create_logger

app = Flask(__name__)
logger = create_logger(app)

titres = {
    'fr_CA': 'Bonjour, bienvenue sur notre site !',
    'en_CA': 'Hello, welcome to our Canadian website!',
    'en_US': 'Hello, welcome to our US website!'
}

def get_locale():
    return request.cookies.get('langue', 'fr_CA')

@app.route('/')
def index():
    """Page d'index"""

    langue = get_locale()
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT s.id_service,s.titre,s.localisation, c.nom_categorie FROM services s' \
                ' join categories c on s.id_categorie = c.id_categorie WHERE s.actif=1 ORDER BY s.date_creation DESC LIMIT 5')
                services = curseur.fetchall()

        date_du_jour = dates.format_date(date.today(), format='long', locale=langue)
        prix_exemple = numbers.format_currency(123.45, 'CAD' if 'CA' in langue else 'USD', locale=langue)
        titre_page = titres.get(langue, titres['fr_CA'])

        return render_template('index.jinja', services=services,
            date_du_jour = date_du_jour,
            prix_exemple =prix_exemple,
            titre_page= titre_page,
            langue=langue)
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
            curseur.execute('SELECT s.id_service, s.titre, s.description ,s.localisation,s.date_creation, s.actif,s.cout, s.photo, nom_categorie as categorie FROM services s ' \
            'join categories  on s.id_categorie =c.id_categorie WHERE s.id_service=%(id)s', {'id': identifiant})
            service = curseur.fetchone()
            if not service:
             abort(404,f"Service avec ID {identifiant}non trouvé") 
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
 
                    if not titre or len(titre) > 50 or caracteres_interdits.search(titre):
                        class_titre = 'is-invalid'
                    if not localisation or len(localisation)>50 or caracteres_interdits.search(localisation) :
                        class_localisation = 'is-invalid'
                    if not description or not(5 <= len(description) <=2000) or caracteres_interdits.search(description):
                        class_description = 'is-invalid'
                    
                    if not cout or float(cout) < 0:
                        class_cout = 'is-invalid'
                    if not categorie or not any(str(cat['id_categorie']) == categorie for cat in categories):
                        class_categorie = 'is-invalid'
                    if not nom_photo or not format_image.search(nom_photo):
                        class_nom_photo = 'is-invalid'
                    if not class_titre or class_localisation or class_description or class_cout  or class_categorie or class_nom_photo:
                        abort(400, "Erreur de validation des champs. Veuillez corriger les erreurs.")
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
                    return redirect('/confirmation', code=303)
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
        return render_template('ajout.jinja', categories=[], titre=titre, localisation=localisation, description=description, cout=cout, statut=statut, nom_photo=nom_photo,categorie=categorie), 500


@app.route('/confirmation')
def redirection_confirmation():
    """Redirection après l'ajout d'un service"""
    return render_template('confirmation.jinja')

@app.route('/modifier', methods=['GET', 'POST'])
def modifier_service():
    """ Modifier les services de la base de données"""
    identifiant = request.args.get('id', type =int)
    if not identifiant:
        abort(400, "Paramètre ID manquant")
    
    caracteres_interdits = re.compile('<|>')
    format_image = re.compile(r'^[\w,\s-]+\.(jpg|jpeg|png|gif)$', re.IGNORECASE)
    class_titre =''
    class_localisation =''
    class_description = ''
    class_cout = ''
    class_nom_photo = ''
    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            curseur.execute("""
                SELECT s.id_service, s.titre, s.description, s.localisation, s.date_creation, s.cout, s.actif, s.photo, c.nom_categorie 
                FROM services s join categories c on s.id_categorie = c.id_categorie WHERE s.id_service =%s""",(identifiant,))
            service = curseur.fetchone()
   
    if not service:
        abort(404, f"Serveice avec ID{identifiant} non trouvé")

    titre = service["titre"]
    localisation = service["localisation"]
    description = service["description"]
    cout = service["cout"]
    statut = str(service["actif"])
    photo = service["photo"]

    if request.method == 'POST':
        titre = request.form.get('titre', '').strip()
        localisation = request.form.get('localisation', '').strip()
        description = request.form.get('description', '').strip()
        cout = request.form.get('cout', '').strip()
        statut = 1 if request.form.get('statut') =='1' else 0
        photo = request.form.get('photo', '').strip()

        if not titre or len(titre) > 50 or caracteres_interdits.search(titre):
            class_titre = 'is-invalid'
        if not localisation or len(localisation) > 50 or caracteres_interdits.search(localisation):
            class_localisation = 'is-invalid'
        if not description or not (5 <= len(description) <= 2000) or caracteres_interdits.search(description):
            class_description = 'is-invalid'
        if not cout or float(cout) < 0:
            class_cout = 'is-invalid'
        if not photo or not format_image.search(photo):
            class_nom_photo = 'is-invalid'

        if not (class_titre or class_localisation or class_description or class_cout or class_nom_photo):
            try:
                with bd.creer_connexion() as conn:
                    with conn.get_curseur() as curseur:
                        curseur.execute("""
                            UPDATE services
                            SET titre=%s, localisation=%s, description=%s, cout=%s, actif=%s, photo=%s
                            WHERE id_service=%s
                            """, (titre, localisation,description, cout, statut,photo, identifiant))
                return redirect('/', code=303)
            except Exception as e:
                abort(500, f"Erreur lors de la mise à jour : {e}")
    return render_template('modifier.jinja',
        service = service,
        titre=titre,
        localisation=localisation,
        description=description,
        cout=cout,
        statut=str(statut),
        photo=photo,
        class_titre=class_titre,
        class_localisation=class_localisation,
        class_description=class_description,
        class_cout=class_cout,
        class_nom_photo=class_nom_photo)
@app.route('/liste')
def liste_service():
    """Afficher les services de la base de données"""
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT s.id_service,s.titre,s.localisation, c.nom_categorie FROM services s' \
                ' join categories c on s.id_categorie = c.id_categorie ORDER BY s.date_creation DESC ')
                services = curseur.fetchall()  
        return render_template('liste.jinja', services=services)
    except Exception as e:
        print(e)    
        return render_template('erreur.jinja' , message =f"Erreur de connexion à la base de données"),500

@app.errorhandler(400)
def erreur_400(e):
    logger.warning(f"Erreur 400: {e}")
    return render_template('erreur.jinja', message=f"Erreur 400 : {e}"), 400

@app.errorhandler(404)
def erreur_404(e):
    logger.warning(f"Erreur 404: {e}")
    return render_template('erreur.jinja', message=f"Erreur 404 : Page non trouvée ou service inexistant"), 404

@app.errorhandler(500)
def erreur_500(e):
    logger.exception(f"Erreur 500:{e}")
    return render_template('erreur.jinja', message=f"Erreur 500 : Problème serveur ou base de données. Veuillez réessayer plus tard"), 500

@app.route('/choisir_langue')
def choisir_langue():
    """Change la langue et l'enregistre dans un cookie"""
    lang = request.args.get('langue', default='fr_CA')
    if lang not in ['fr_CA', 'en_CA', 'en_US']:
        lang = 'fr_CA'  # fallback
    
    reponse = make_response(redirect('/'))
    reponse.set_cookie('langue', lang)
    return reponse
 
if __name__ == '__main__':
    app.run(debug=True)
