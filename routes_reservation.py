from flask import Blueprint, render_template, request, redirect, flash, session, abort, current_app as app, url_for
import bd

bp_reservation = Blueprint('reservation', __name__)

@bp_reservation.route("/reserver/<int:id_service>", methods=["GET", "POST"])
def reserver_service(id_service):
    """Réserver un service pour un utilisateur connecté"""

    id_utilisateur = session.get("id_utilisateur")
    if not id_utilisateur:
        flash("Vous devez être connecté pour réserver un service.", "error")
        return redirect(url_for("comptes.connexion"))

    try:
        with bd.creer_connexion() as conn:
            service = bd.obtenir_service_par_id(conn, id_service)
            if not service:
                abort(404, "Service introuvable.")

            if service.get("actif") != 1:
                abort(403, "Ce service est inactif et ne peut pas être réservé.")

            if service.get("id_proprietaire") == id_utilisateur:
                flash("Vous ne pouvez pas réserver votre propre service.", "error")
                return redirect(url_for("services.liste"))

            utilisateur = bd.obtenir_utilisateur_par_id(conn, id_utilisateur)
            if not utilisateur:
                abort(404, "Utilisateur introuvable.")

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

    except Exception as e:
        app.logger.error(f"Erreur lors de la réservation du service {id_service}: {e}")
        abort(500, "Erreur serveur.")

@bp_reservation.route("/verifier_disponibilite/<int:id_service>")
def api_verifier_dispo(id_service):
    date_heure = request.args.get("date_heure")
    if not date_heure:
        return {"erreur": "date_heure manquante"}, 400

    try:
        with bd.creer_connexion() as conn:
            dispo = bd.verifier_disponibilite(conn, id_service, date_heure)
        return {"disponible": dispo}, 200

    except Exception as e:
        return {"erreur": str(e)}, 500