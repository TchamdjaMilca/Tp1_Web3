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
            SELECT * FROM utilisateurs
        """)
        return curseur.fetchall()

def liste_services(conn):
    """Retourne la liste complète des utilisateurs."""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT * FROM services
        """)
        return curseur.fetchall()

def ajouter_utilisateurs(conn, courriel, mot_de_passe, nom, prenom):
    """"""
    with conn.get_curseur() as curseur:
        curseur.execute("""INSERT INTO utilisateurs (courriel, mot_de_passe, nom, prenom, credit)
        VALUES (%s, %s, %s, %s, 0) """, (courriel, mot_de_passe, nom, prenom),)     

def supprimer_service(connexion, id_service, id_utilisateur):
    """
    Supprime un service seulement si :
    - il appartient à l'utilisateur
    - il n'a pas encore été réservé 
    Retourne True si la suppression a réussi, False sinon.
    """
    try:
        with connexion.cursor(dictionary=True) as curseur:
            requete = """
                
                )
            """
            curseur.execute(requete, (id_service, id_utilisateur))
            connexion.commit()
            return curseur.rowcount > 0
    except Exception as e:
        print(e) 
def supprimer_service(conn, id_service, id_proprietaire):
    """Supprime un service seulement si :il appartient à l'utilisateur, il n'a pas encore été réservé. Retourne True si la suppression a réussi, False sinon."""
    with conn.get_curseur() as curseur:
        curseur.execute(""" DELETE FROM services WHERE id_service = %s AND id_proprietaire = %s AND id_service NOT IN
         (SELECT id_service FROM reservations)""", (id_service, id_proprietaire))
        conn.commit()
        return curseur.rowcount > 0
def supprimer_utilisateur(conn, id_utilisateur):
    """Supprimer un utilisateur. """
    with conn.get_curseur() as curseur:
        curseur.execute(
            "DELETE FROM utilisateurs WHERE id_utilisateur = %s",
            (id_utilisateur,)
        )
def verifier_disponibilite(conn,id_service, date_reservation, heure_reservation):
    """Vérifie si le service est libre à ce moment-là."""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT COUNT(*) AS total
            FROM reservations
            WHERE id_service = %s
            AND date_reservation = %s
            AND heure_reservation = %s
        """, (id_service, date_reservation, heure_reservation))
        resultat = curseur.fetchone()
        return resultat["total"] == 0
def chercher_service_par_id(conn, id_service):
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * FROM services WHERE id_service = %s", (id_service,))
        return curseur.fetchone()
