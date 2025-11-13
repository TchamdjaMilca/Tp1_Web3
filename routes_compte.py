from flask import Blueprint,  render_template, request, redirect,url_for, session,flash, current_app as app

from utilitaires import hacher_mdp
import bd
import re


bp_compte= Blueprint('comptes', __name__)

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

        if not courriel:
            erreur["courriel"] = "Veuillez entrer votre courriel."
        elif not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', courriel):
            erreur["courriel"] = "Le courriel n’est pas valide."

        if not mdp_brut:
          erreur["mot_de_passe"] = "Veuillez entrer votre mot de passe."

        if not erreur:
            mdp_hache = hacher_mdp(mdp_brut)
            try:
                with bd.creer_connexion() as conn:
                    utilisateur = bd.chercher_utilisateur(conn, courriel, mdp_hache)

                    if utilisateur:
                        session["id_utilisateur"] = utilisateur["id_utilisateur"]   
                        session["utilisateur"] = utilisateur["courriel"]
                        session["nom"] = utilisateur["nom"]
                        session["est_admin"] = utilisateur["est_admin"]

                        flash(f"Bienvenue {utilisateur['nom']} !")
                        if utilisateur["est_admin"]:
                         return render_template('comptes/admin.jinja', utilisateur=utilisateur)
                        else:
                            return render_template('comptes/utilisateur.jinja', utilisateur=utilisateur)
                    else:
                        flash("Courriel ou mot de passe incorrect.","error")
            except Exception as e:
                app.logger.exception("Erreur BD lors de l'authentification: %s", e)
                flash("Erreur serveur. Réessayez plus tard.")
    return render_template('comptes/connecter.jinja', erreur=erreur, courriel=courriel)

bp_service = Blueprint('services', __name__)

@bp_compte.route("/liste_utilisateurs")
def liste_utilisateurs():
   """helos"""
   with bd.creer_connexion() as connexion:
                utilisateurs = bd.liste_utilisateurs(connexion)
                print(utilisateurs)
                return render_template("comptes/liste_utilisateurs.jinja", utilisateurs = utilisateurs)
@bp_compte.route('/deconnexion')
def deconnexion():
    """Déconnecte l'utilisateur"""
    nom = session.get("nom")
    session.clear()
    if nom:
        flash(f"{nom} a été déconnecté avec succès.", "info")
    else:
        flash("Aucun utilisateur n'était connecté.", "warning")
    return redirect(url_for('services.liste'))



@bp_compte.route("/form_ajout_compter")
def form_ajout_compter():
   return render_template("comptes/ajout_compte.jinja")
@bp_compte.route("/ajouter_compte", methods=["GET", "POST"])
def ajouter_compte():
    if request.method == "POST":
        caracteres_interdits = re.compile('<|>')
        regex_courriel = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        regex_mot_de_passe = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        erreur = False
        nom = request.form.get("nom","").strip()
        prenom = request.form.get("prenom","").strip()
        courriel = request.form.get("courriel","").strip()
        mot_de_passe = request.form.get("mot_de_passe", "").strip()
        confirmation_dot_de_passe = request.form.get("confirmation_mot_de_passe", "").strip()
        if not nom or caracteres_interdits.search(nom):
            flash("Veuillez entrer un nom valide","nom")
            erreur = True
        if not prenom or caracteres_interdits.search(prenom):
            flash("Veuillez entrer un prenom valide","prenom")
            erreur = True
        if not courriel or not re.match(regex_courriel, courriel):
            flash("Veuillez entrer un courriel valide.", "courriel")
            erreur = True
        if not mot_de_passe or not re.match(regex_mot_de_passe, mot_de_passe):
            flash("Veuillez entrer un mot de passe valide (au moins 8 caractères, avec majuscule, minuscule et chiffre).", "mot_de_passe")
            erreur = True
        if mot_de_passe != confirmation_dot_de_passe:
            flash("Veuillez confirmer correctement votre mot de passe.", "confirmation_mot_de_passe")
            erreur = True
        if erreur:
            return render_template("comptes/ajout_compte.jinja", confirmation_dot_de_passe = confirmation_dot_de_passe, courriel = courriel, mot_de_passe = mot_de_passe,nom = nom, prenom = prenom )
        mot_de_passe = hacher_mdp(mot_de_passe)
        with bd.creer_connexion() as connexion:
            utilisateur = bd.chercher_utilisateur(connexion, courriel,mot_de_passe)
            if utilisateur:
               flash("L'utilisateur existe déjà.","utilisateur_existe")
               return render_template("comptes/ajout_compte.jinja", confirmation_dot_de_passe = confirmation_dot_de_passe, courriel = courriel, mot_de_passe = mot_de_passe,nom = nom, prenom = prenom )
            bd.ajouter_utilisateurs(connexion,courriel, mot_de_passe, nom, prenom)
            return redirect(url_for("comptes.liste_utilisateurs"))

    if not erreur:
        with bd.creer_connexion() as connexion:
            bd.ajouter_utilisateurs(connexion,courriel, mot_de_passe, nom, prenom)
            return redirect("comptes/liste_utilisateurs.jinja")


@bp_compte.route("/supprimer_compte/<int:id_utilisateur>", methods=["POST"])
def supprimer_compte(id_utilisateur):
    """Permet à l’administrateur de supprimer un compte"""

    if "utilisateur" not in session:
        flash("Vous devez être connecté pour effectuer cette action.")
        return redirect("/comptes/connexion")

    if session.get("est_admin") != 1:
        flash("Accès réservé à l’administrateur.")
        return redirect("/")

    try:
        with bd.creer_connexion() as conn:
            bd.supprimer_utilisateur(conn, id_utilisateur)
            flash("Le compte a été supprimé avec succès.")
    except Exception as e:
        app.logger.exception("Erreur BD lors de la suppression du compte: %s", e)
        flash("Erreur serveur. Réessayez plus tard.")

    return redirect(url_for("comptes.liste_utilisateurs"))

