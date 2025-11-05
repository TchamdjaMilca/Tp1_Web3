from flask import Blueprint,  render_template, request, redirect,url_for, session,flash, current_app as app

from utilitaires import hacher_mdp
import bd

bp_compte= Blueprint('comptes', __name__)
bp_service =Blueprint('services', __name__)


@bp_compte.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Permet à l'utilisateur de se connecter"""
    courriel = ""
    mdp_brut = ""
    erreur = {}

    if request.method == 'POST':
        courriel = request.form.get("courriel", "").strip()
        mdp_brut = request.form.get("mot_de_passe", "").strip()

        app.logger.info("Début d'authentification pour %s", courriel)

        # Validation des champs
        if not courriel:
            erreur["courriel"] = "Le courriel est invalide."
        if not mdp_brut:
            erreur["mot_de_passe"] = "Le mot de passe est invalide."

        if not erreur:
            mdp_hache = hacher_mdp(mdp_brut)
            print("DEBUG login:", courriel, mdp_hache)
            try:
                with bd.creer_connexion() as conn:
                    utilisateur = bd.chercher_utilisateur(conn, courriel, mdp_hache)

                    if utilisateur:
                        session["utilisateur"] = utilisateur["courriel"]
                        session["nom"] = utilisateur["nom"]
                        session["est_admin"] = utilisateur["est_admin"]

                        flash(f"Bienvenue {utilisateur['nom']} !", "success")
                        print (utilisateur["est_admin"], "allo")
                        if utilisateur["est_admin"]:
                            return render_template('comptes/admin.jinja', utilisateur=utilisateur)
                        else: 
                           return render_template('comptes/utilisateur.jinja', utilisateur=utilisateur)

                    else:
                        flash("Courriel ou mot de passe incorrect.", "danger")
            except Exception as e:
                app.logger.exception("Erreur BD lors de l'authentification: %s", e)
                flash("Erreur serveur. Réessayez plus tard.", "danger")
        else:
           
            for champ, message in erreur.items():
                print(f"Erreur dans {champ}: {message}")

    return render_template('comptes/connecter.jinja', erreur=erreur, courriel=courriel)

bp_service = Blueprint('services', __name__)

# @bp_service.route('/liste')
# def liste():
#     ...


@bp_compte.route('/deconnecter', methods=['GET'])
def deconnecter():
    """deconnecter"""
    if "utilisateur" in session:
        nom = session.get("nom") or session.get("utilisateur")
        session.clear()
        flash(f"{nom} a été déconnecté avec succès.", "info")
    else:
        flash("Aucun utilisateur n'était connecté.", "warning")

    return redirect("/") 

@bp_compte.route('/liste_utilisateurs')
def liste_utilisateurs():
    """Affiche la liste des utilisateurs (réservé à l’administrateur)"""
    # Vérifie si un utilisateur est connecté
    if "utilisateur" not in session:
        flash("Veuillez vous connecter d’abord.", "warning")
        return render_template("comptes/connecter.jinja")

    # Vérifie si c’est un administrateur
    if not session.get("est_admin"):
        flash("Accès refusé : réservé à l’administrateur.", "danger")
        return render_template("comptes/utilisateur.jinja", utilisateur={"nom": session["nom"]})

    try:
        with bd.creer_connexion() as conn:
            utilisateurs = bd.liste_utilisateurs(conn)
    except Exception as e:
        app.logger.exception("Erreur BD lors de la récupération des utilisateurs: %s", e)
        flash("Erreur lors du chargement des utilisateurs.", "danger")
        utilisateurs = []

    return render_template("comptes/liste_utilisateurs.jinja", utilisateurs=utilisateurs)
