"""
Pour démontrer l'utilisation des templates
"""
 
import random
import os
 
from flask import Flask, render_template, request , abort  , redirect , make_response,session
import re
import bd
from flask_babel import Babel,numbers, dates
from flask.logging import create_logger
from datetime import date
 
from routes_compte import bp_compte
from routes_reservation import bp_reservation
from routes_service import bp_service
 
app = Flask(__name__)
app.register_blueprint(bp_service, url_prefix='/services')
app.register_blueprint(bp_compte, url_prefix='/comptes')
app.register_blueprint(bp_reservation, url_prefix='/reservation')
 
app.config['MORCEAUX_VERS_IMAGES'] = ["static", "images"]
app.config['ROUTE_VERS_IMAGES'] = "/".join(app.config['MORCEAUX_VERS_IMAGES'])
app.config['CHEMIN_VERS_IMAGES'] = os.path.join(app.root_path, *app.config['MORCEAUX_VERS_IMAGES'])

logger = create_logger(app)
 
app.secret_key = "Cette chaîne servira pour l'encryption de la session. \
                  Elle doit être générée aléatoirement"
# app.secret_key ="e81ea91a141620d25a70f65c4d02e81d1a5fa7c8a5bc8fa8df6eda83300402ad"
 
titres = {
    'fr_CA': 'Bonjour, bienvenue sur notre site !',
    'en_CA': 'Hello, welcome to our Canadian website!',
    'en_US': 'Hello, welcome to our US website!'
}
 
def get_locale():
    return request.cookies.get('langue', 'fr_CA')
 
@app.route('/')
def index():
    """Page d'accueil : affiche les 5 derniers services"""
    try:
        with bd.creer_connexion() as conn:
            services = bd.obtenir_services_recents(conn)
        for s in services:
            if s.get("photo"):
                s["src"] = f"/{app.config['ROUTE_VERS_IMAGES']}/{s['photo']}"
    except Exception as e:
        logger.error(f"Erreur BD: {e}")
        abort(500)
    return render_template('index.jinja', services=services)

@app.errorhandler(400)
def erreur_400(e):
    """Logger erreur 400"""
    logger.warning(f"Erreur 400: {e}")
    return render_template('erreur/erreur.jinja', message=f"Erreur 400 : {e}"), 400
 
@app.errorhandler(404)
def erreur_404(e):
    """Logger erreur 404"""
    logger.warning(f"Erreur 404: {e}")
    return render_template('erreur/erreur.jinja', message=f"Erreur 404 : Page non trouvée ou service inexistant"), 404
@app.errorhandler(401)
def erreur_401(e):
    """Affiche une page 401 avec un lien vers la connexion"""
    logger.warning(f"Erreur 401: {e}")
    return render_template(
        "erreur/erreur.jinja",
        message="Vous devez être connecté pour accéder à cette page.",
    ), 401
 
 
@app.errorhandler(500)
def erreur_500(e):
    """Logger erreur 500"""
    logger.exception(f"Erreur 500:{e}")
    return render_template('erreur/erreur.jinja', message=f"Erreur 500 : Problème serveur ou base de données. Veuillez réessayer plus tard"), 500
 
@app.route('/choisir_langue')
def choisir_langue():
    """Change la langue et l'enregistre dans un cookie"""
    lang = request.args.get('langue', default='fr_CA')
    if lang not in ['fr_CA', 'en_CA', 'en_US']:
        lang = 'fr_CA'
   
    reponse = make_response(redirect('/'))
    reponse.set_cookie('langue', lang)
    return reponse
 
if __name__ == '__main__':
    app.run(debug=True)