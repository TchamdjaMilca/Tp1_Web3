from flask import Blueprint,  render_template, request, redirect,abort,flash

import bd

bp_reservation = Blueprint('reservation', __name__)

@bp_reservation.route('/reservation', methods=['GET'])
def reservation():
    """deconnecter"""
    return render_template("reservation/reservation.jinja")

@bp_reservation.route("/services/reserver", methods=["GET", "POST"])
def reserver_service():
    id_service = request.args.get("id", type=int)
    if not id_service:
        abort(400, "ID du service manquant")

    with bd.creer_connexion() as conn:
        service = bd.chercher_service_par_id(conn, id_service)
        if not service:
            abort(404, "Service non trouvé")

        if request.method == "POST":
            date_reservation = request.form.get("date_reservation")
            heure_reservation = request.form.get("heure_reservation")

            if not date_reservation or not heure_reservation:
                flash("Choisis une date et une heure.")
            else:
                libre = bd.verifier_disponibilite(conn, id_service, date_reservation, heure_reservation)
                if libre:
                    flash("Ce créneau est disponible.")
                else:
                    flash("Ce créneau est déjà réservé.")

    return render_template("reservation/reservation.jinja", service=service)
