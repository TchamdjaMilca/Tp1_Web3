from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, current_app as app
from utilitaires import hacher_mdp
import bd
import re

bp_compte = Blueprint('comptes', __name__)


@bp_compte.route('/Espace_utilisateur')
def Espace_utilisateur():
    if "id_utilisateur" not in session:
        abort(401)

    return render_template('comptes/utilisateur.jinja')

@bp_compte.route('/connexion', methods=['GET', 'POST'])
def connexion():
    courriel = ""
    mdp_brut = ""
    erreur = {}

    if request.method == 'POST':
        courriel = request.form.get("courriel", "").strip()
        mdp_brut = request.form.get("mot_de_passe", "").strip()

        app.logger.info("Début d'authentification pour %s", courriel)

        if not courriel:
            erreur["courriel"] = "Veuillez entrer votre courriel."
        elif not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', courriel):
            erreur["courriel"] = "Courriel invalide."

        if not mdp_brut:
            erreur["mot_de_passe"] = "Veuillez entrer votre mot de passe."

        if not erreur:
            mdp_hache = hacher_mdp(mdp_brut)
            try:
                with bd.creer_connexion() as conn:
                    utilisateur = bd.chercher_utilisateur(conn, courriel, mdp_hache)
            except Exception as e:
                app.logger.error(e)
                abort(500)

            if utilisateur:
                session["id_utilisateur"] = utilisateur["id_utilisateur"]
                session["utilisateur"] = utilisateur["courriel"]
                session["nom"] = utilisateur["nom"]
                session["est_admin"] = bool(utilisateur["est_admin"])

                flash(f"Bienvenue {utilisateur['nom']} !")

                if utilisateur["est_admin"]:
                    return render_template('comptes/admin.jinja', utilisateur=utilisateur)
                else:
                    return render_template('comptes/utilisateur.jinja', utilisateur=utilisateur)

            else:
                flash("Courriel ou mot de passe incorrect.", "error")

    return render_template('comptes/connecter.jinja', erreur=erreur, courriel=courriel)

@bp_compte.route("/liste_utilisateurs")
def liste_utilisateurs():
    if "id_utilisateur" not in session:
        abort(401)

    if not session.get("est_admin"):
        abort(403)

    try:
        with bd.creer_connexion() as conn:
            utilisateurs = bd.liste_utilisateurs(conn)
    except Exception as e:
        app.logger.error(e)
        abort(500)
    utilisateur = {
        "nom": session.get("nom"),
        "courriel": session.get("utilisateur"),
        "est_admin": session.get("est_admin")
    }
    return render_template("comptes/liste_utilisateurs.jinja", utilisateurs=utilisateurs,   utilisateur=utilisateur)

@bp_compte.route('/deconnexion')
def deconnexion():
    nom = session.get("nom")
    session.clear()
    flash(f"{nom} a été déconnecté avec succès.", "info")
    return redirect(url_for('index')) 

@bp_compte.route("/form_ajout_compter")
def form_ajout_compter():
    if "id_utilisateur" not in session:
        abort(401)

    if not session.get("est_admin"):
        abort(403)

    return render_template("comptes/ajout_compte.jinja")


@bp_compte.route("/ajouter_compte", methods=["POST"])
def ajouter_compte():

    if "id_utilisateur" not in session:
        abort(401)

    if not session.get("est_admin"):
        abort(403)

    caracteres_interdits = re.compile('<|>')
    regex_courriel = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    regex_mot_de_passe = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

    nom = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    courriel = request.form.get("courriel", "").strip()
    mot_de_passe = request.form.get("mot_de_passe", "").strip()
    confirmation = request.form.get("confirmation_mot_de_passe", "").strip()

    if (not nom or caracteres_interdits.search(nom) or
        not prenom or caracteres_interdits.search(prenom) or
        not courriel or not re.match(regex_courriel, courriel) or
        not mot_de_passe or not re.match(regex_mot_de_passe, mot_de_passe) or
        mot_de_passe != confirmation):
        abort(400)

    mot_de_passe_hache = hacher_mdp(mot_de_passe)

    try:
        with bd.creer_connexion() as conn:
            bd.ajouter_utilisateurs(conn, courriel, mot_de_passe_hache, nom, prenom)
    except Exception as e:
        app.logger.error(e)
        abort(500)

    return redirect(url_for("comptes.liste_utilisateurs"))

@bp_compte.route('/admin')
def admin():
    if "id_utilisateur" not in session:
        abort(401)
    if not session.get("est_admin"):
        abort(403)

    utilisateur = {
        "nom": session.get("nom"),
        "courriel": session.get("utilisateur"),
        "est_admin": session.get("est_admin")
    }

    return render_template("comptes/admin.jinja", utilisateur=utilisateur)



@bp_compte.route("/supprimer_compte/<int:id_utilisateur>", methods=["POST"])
def supprimer_compte(id_utilisateur):

    if "id_utilisateur" not in session:
        abort(401)

    if not session.get("est_admin"):
        abort(403)

    try:
        with bd.creer_connexion() as conn:
            utilisateur = bd.obtenir_utilisateur_par_id(conn, id_utilisateur)
    except Exception:
        abort(500)

    if utilisateur is None:
        abort(404)

    try:
        with bd.creer_connexion() as conn:
            bd.supprimer_utilisateur(conn, id_utilisateur)
    except Exception:
        abort(500)

    return redirect(url_for("comptes.liste_utilisateurs"))
