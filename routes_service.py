from flask import Blueprint,  render_template, request, redirect,flash,session,url_for

import bd

bp_service = Blueprint('services', __name__)


@bp_service.route("/liste")
def afficher_liste_services():
   """"""
   with bd.creer_connexion() as connexion:
                services = bd.liste_services(connexion)
                return render_template("services/liste.jinja", services = services)
@bp_service.route("/supprimer/<int:id_service>")
def supprimmer_service(id_service):
    """Permet à un utilisateur de supprimer un service qu'il a ajouté et non réservé"""

    id_utilisateur = session.get("id_utilisateur")
    
    with bd.creer_connexion() as connexion:
        succes = bd.supprimer_service(connexion, id_service, id_utilisateur)
        if succes:
            flash(" Service supprimé avec succès.", "succes")
        else:
            flash(" Impossible de supprimer ce service déjà réservé .", "Impossible")

    return redirect(url_for("services.afficher_liste_services"))
