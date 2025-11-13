from flask import Blueprint, render_template, request, redirect, abort, flash, current_app as app, session, url_for
import bd

bp_reservation = Blueprint('reservation', __name__)

@bp_reservation.route("/services/reserver/<int:id_service>", methods=["GET", "POST"])
def reserver_service(id_service):
    """Permet à un utilisateur authentifié de réserver un service"""

    id_utilisateur = session.get("id_utilisateur")
    if not id_utilisateur:
        flash("Vous devez être connecté pour réserver un service.", "error")
        return redirect(url_for("comptes.connexion"))

    with bd.creer_connexion() as conn:
        service = bd.obtenir_service_par_id(conn, id_service)
        if not service:
            abort(404, "Service introuvable.")

        if service.get("id_proprietaire") == id_utilisateur:
            flash("Vous ne pouvez pas réserver votre propre service.", "error")
            return redirect(url_for("services.liste"))

        utilisateur = bd.obtenir_utilisateur_par_id(conn, id_utilisateur)
        if not utilisateur:
            flash("Utilisateur non trouvé.", "error")
            return redirect(url_for("services.liste"))

        if utilisateur["credit"] < service["cout"]:
            flash("Crédit insuffisant pour réserver ce service.", "error")
            return render_template("reservation/reservation.jinja", service=service)

        if request.method == "POST":
            date_heure_reservation = request.form.get("date_heure_reservation")

            if not date_heure_reservation:
                flash("Veuillez choisir une date et une heure.", "error")
                return render_template("reservation/reservation.jinja", service=service)

            disponible = bd.verifier_disponibilite(conn, id_service, date_heure_reservation)
            if not disponible:
                flash("Ce créneau est déjà réservé.", "error")
                return render_template("reservation/reservation.jinja", service=service)

            bd.ajouter_reservation(conn, id_utilisateur, id_service, date_heure_reservation)

            bd.mettre_a_jour_credits(conn, id_utilisateur, service["id_proprietaire"], service["cout"])

            flash("Réservation effectuée avec succès !", "success")
            return render_template(
                "reservation/confirmation_reservation.jinja",
                service=service,
                date_heure_reservation=date_heure_reservation
            )
    return render_template("reservation/reservation.jinja", service=service)
