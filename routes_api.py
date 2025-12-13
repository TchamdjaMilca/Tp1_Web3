import time
import random
from flask import Blueprint, jsonify, session, render_template, request, redirect, abort

import bd

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/utilisateurs", methods=["GET"])
def api_rechercher_utilisateurs():
    email = request.args.get("email", "").strip()

    if len(email) < 4:
        return jsonify([]), 200

    try:
        with bd.creer_connexion() as conn:
            resultats = bd.rechercher_utilisateur(conn, email)
        return jsonify(resultats), 200

    except Exception as e:
        return jsonify({"erreur": "Erreur serveur"})
@api.route('/recherche')
def recherche():
    mots_cles = request.args.get('mots-cles', '').strip()

    try:
        with bd.creer_connexion() as conn:
            services = bd.rechercher_services(conn, mots_cles)
    except Exception as e:
        return jsonify([]), 500

    return jsonify(services)
@api.route("/supprimer/<int:id_service>", methods=["DELETE"])
def api_supprimer_service(id_service):
    try:
        with bd.creer_connexion() as conn:
            id_proprietaire = session.get("id_utilisateur")

            succes = bd.supprimer_service(conn, id_service, id_proprietaire)

        if not succes:
            return jsonify({"succes": False, "message": "Impossible de supprimer ce service, car il possède des réservations"})

        return jsonify({"succes": True})

    except Exception :
        return jsonify({"succes": False, "message": "Erreur serveur"})

@api.route("/utilisateurs/<int:id_utilisateur>", methods=["DELETE"])
def api_supprimer_utilisateur(id_utilisateur):

    if "id_utilisateur" not in session:
        return jsonify({"succes": False}), 401

    if not session.get("est_admin"):
        return jsonify({"succes": False}), 403

    try:
        with bd.creer_connexion() as conn:
            utilisateur = bd.obtenir_utilisateur_par_id(conn, id_utilisateur)
            if utilisateur is None:
                return jsonify({"succes": False, "message": "Introuvable"}), 404

            bd.supprimer_utilisateur(conn, id_utilisateur)

        return jsonify({"succes": True})

    except Exception:
        return jsonify({"succes": False, "message": "Erreur serveur"}), 500
