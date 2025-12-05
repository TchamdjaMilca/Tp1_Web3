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
        print("Erreur BD", e)
        return jsonify({"erreur": "Erreur serveur"}), 500
