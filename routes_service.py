from flask import Blueprint,  render_template, request, redirect,flash,session,url_for, abort, current_app as app
 
import bd
import os
import re
from utilitaires import valider_service
bp_service = Blueprint('services', __name__)
 
 
@bp_service.route('/liste')
def liste():
    """Affiche la liste complète des services"""
    try:
        with bd.creer_connexion() as conn:
            services = bd.obtenir_tous_les_services(conn)
    except Exception as e:
        app.logger.error(f"Erreur BD dans /liste : {e}")
        abort(500, "Erreur de connexion à la base de données")
    return render_template('services/liste.jinja', services=services)
 
 
 
@bp_service.route('/details/<int:id_service>')
def details(id_service):
    """Affiche les détails d’un service"""
    try:
        with bd.creer_connexion() as conn:
            service = bd.obtenir_details_service(conn, id_service)
    except Exception as e:
        app.logger.error(f"Erreur BD dans /details/{id_service} : {e}")
        abort(500, "Erreur de connexion à la base de données")
 
    if not service:
        abort(404, f"Service avec ID {id_service} non trouvé")
 
    if service.get("photo"):
        service["src"] = f"/{app.config['ROUTE_VERS_IMAGES']}/{service['photo']}"
 
    return render_template('services/details.jinja', service=service)
 
 
@bp_service.route('/ajout', methods=['GET', 'POST'])
def ajouter_service():
    """Ajout d’un service avec validation"""
    id_proprietaire = session.get("id_utilisateur")
    if not id_proprietaire:
        abort(401, "Authentification requise")
 
    titre = ''
    localisation = ''
    description = ''
    cout = ''
    categorie = ''
    statut = 1
    class_titre = ''
    class_localisation = ''
    class_description = ''
    class_cout = ''
    class_categorie = ''
    class_photo = ''
 
    try:
        with bd.creer_connexion() as conn:
            categories = bd.obtenir_categories(conn)
 
            if request.method == 'POST':
                titre = request.form.get('titre', '').strip()
                localisation = request.form.get('localisation', '').strip()
                description = request.form.get('description', '').strip()
                cout = request.form.get('cout', '').strip()
                statut = 1 if request.form.get('statut') == '1' else 0
                categorie = request.form.get('categorie', '').strip()
                photo = request.files.get('photo')
 
                if not titre or len(titre) > 50:
                    class_titre = 'is-invalid'
                if not localisation or len(localisation) > 50:
                    class_localisation = 'is-invalid'
                if not description or not (5 <= len(description) <= 2000):
                    class_description = 'is-invalid'
                if not cout or float(cout) < 0:
                    class_cout = 'is-invalid'
 
                if not categorie or not any(str(cat['id_categorie']) == categorie for cat in categories):
                    class_categorie = 'is-invalid'
                if not photo or not re.match(r'^[\w,\s-]+\.(jpg|jpeg|png|gif)$', photo.filename, re.IGNORECASE):
                    class_photo = 'is-invalid'
 
                if not any([class_titre, class_localisation, class_description, class_cout, class_categorie, class_photo]):
                    chemin_complet = os.path.join(app.config['CHEMIN_VERS_IMAGES'], photo.filename)
                    photo.save(chemin_complet)
                    bd.inserer_service(conn, titre, localisation, description, cout, statut, photo.filename, categorie, id_proprietaire)
                    bd.donner_credit_pour_ajout_service(conn, id_proprietaire)
                    return redirect(url_for('services.confirmation', code=303))
 
            return render_template('services/ajout.jinja',
                                   categories=categories,
                                   titre=titre,
                                   localisation=localisation,
                                   description=description,
                                   cout=cout,
                                   statut=statut,
                                   categorie=categorie,
                                   class_titre=class_titre,
                                   class_localisation=class_localisation,
                                   class_description=class_description,
                                   class_cout=class_cout,
                                   class_categorie=class_categorie,
                                   class_photo=class_photo)
    except Exception as e:
        abort(500, f"Erreur BD : {e}")




@bp_service.route('/confirmation')
def confirmation():
    """Page de confirmation générique"""
    return render_template('services/confirmation.jinja')

@bp_service.route("/supprimer/<int:id_service>")
def supprimmer_service(id_service):
    """Permet à un utilisateur de supprimer un service qu'il a ajouté et non réservé"""
 
    id_utilisateur = session.get("id_utilisateur")
   
    with bd.creer_connexion() as connexion:
        succes = bd.supprimer_service(connexion, id_service, id_utilisateur)
        if succes:
            message = " Service supprimé avec succès."
        else:
           message = " Impossible de supprimer ce service déjà réservé ."
 
    return render_template("/services/confirmation.jinja" , message=message, code=303)

@bp_service.route('/modifier/<int:id_service>', methods=['GET', 'POST'])
def modifier_service(id_service):
    """Modification d’un service existant"""
    if("id_utilisateur" not in session):
        abort(401, "Authentification requise")
    try:
        with bd.creer_connexion() as conn:
            service = bd.obtenir_service_par_id(conn, id_service)
            if not service:
                abort(404, f"Service {id_service} introuvable")

            titre = service['titre']
            localisation = service['localisation']
            description = service['description']
            cout = str(service['cout'])
            statut = str(service['actif'])
            photo_nom = service['photo']

            class_titre = ""
            class_localisation = ""
            class_description = ""
            class_cout = ""
            class_nom_photo = ""

            if request.method == 'POST':
                titre = request.form.get('titre', '').strip()
                localisation = request.form.get('localisation', '').strip()
                description = request.form.get('description', '').strip()
                cout = request.form.get('cout', '').strip()
                statut = 1 if request.form.get('statut') == '1' else 0
                photo = request.files.get('photo')

                if not titre or len(titre) > 50:
                    class_titre = 'is-invalid'
                if not localisation or len(localisation) > 50:
                    class_localisation = 'is-invalid'
                if not description or not (5 <= len(description) <= 2000):
                    class_description = 'is-invalid'
                if not cout or float(cout) < 0:
                    class_cout = 'is-invalid'
                if photo and photo.filename:
                    if not re.match(r'^[\w,\s-]+\.(jpg|jpeg|png|gif)$', photo.filename, re.IGNORECASE):
                        class_nom_photo = 'is-invalid'

                if not any([class_titre, class_localisation, class_description, class_cout, class_nom_photo]):
                    if photo and photo.filename:
                        chemin = os.path.join(app.config['CHEMIN_VERS_IMAGES'], photo.filename)
                        photo.save(chemin)
                        photo_nom = photo.filename

                    bd.mettre_a_jour_service(conn, id_service, titre, localisation, description, cout, statut, photo_nom)
                    flash("Service modifié avec succès.", "success")
                    return redirect(url_for('services.liste'), code=303)

            return render_template('services/modifier.jinja',
                                   service=service,
                                   titre=titre,
                                   localisation=localisation,
                                   description=description,
                                   cout=cout,
                                   statut=statut,
                                   class_titre=class_titre,
                                   class_localisation=class_localisation,
                                   class_description=class_description,
                                   class_cout=class_cout,
                                   class_nom_photo=class_nom_photo)
    except Exception as e:
        abort(500, f"Erreur de mise à jour : {e}")

 