"""
Connexion à la BD
"""

import types
import contextlib
import mysql.connector


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user="garneau",
        password="qwerty_123",
        host="127.0.0.1",
        database="services",
        raise_on_warnings=True
    )

    # Pour ajouter la méthode getCurseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()

def chercher_utilisateur(conn, courriel, mdp_hache):
    """Retourne un utilisateur si le courriel et le mot de passe correspondent"""
    print("DEBUG query:", courriel, mdp_hache)

    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT * FROM utilisateurs WHERE courriel=%s AND mot_de_passe=%s",
            (courriel, mdp_hache)
        )
        utilisateur = curseur.fetchone()
        if utilisateur:
            utilisateur["est_admin"] = bool(utilisateur["est_admin"])
        return utilisateur
def liste_utilisateurs(conn):
    """Retourne la liste complète des utilisateurs."""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT id_utilisateur, courriel, nom, prenom, credit, est_admin
            FROM utilisateurs
        """)
        return curseur.fetchall()



