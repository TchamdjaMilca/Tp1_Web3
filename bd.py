"""
COnnexion à la BD
"""

import types
import contextlib
import mysql.connector


@contextlib.contextmanager
def creer_connexion():
    """Crée une connexion à la base de données MySQL"""
    conn = mysql.connector.connect(
        user="garneau",
        password="qwerty_123",
        host="127.0.0.1",
        database="services",
        raise_on_warnings=True
    )

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
    """Permet d’avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()


def chercher_utilisateur(conn, courriel, mdp_hache):
    """Retourne un utilisateur si le courriel et le mot de passe correspondent"""
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
    """Retourne la liste complète des utilisateurs"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * FROM utilisateurs")
        return curseur.fetchall()


def ajouter_utilisateurs(conn, courriel, mot_de_passe, nom, prenom):
    """Ajoute un nouvel utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO utilisateurs (courriel, mot_de_passe, nom, prenom, credit)
            VALUES (%s, %s, %s, %s, 0)
        """, (courriel, mot_de_passe, nom, prenom))


def supprimer_utilisateur(conn, id_utilisateur):
    """Supprime un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute("DELETE FROM reservations WHERE id_utilisateur = %s",(id_utilisateur,) )
        curseur.execute("DELETE FROM services WHERE id_proprietaire = %s",(id_utilisateur,))
        curseur.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s",(id_utilisateur,))
       


def obtenir_services_recents(conn, limit = 5):
    """Retourne les derniers services actifs"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT *
            FROM services s
            JOIN categories c ON s.id_categorie = c.id_categorie
            WHERE s.actif = 1
            ORDER BY s.date_creation DESC
            LIMIT %s
        """, (limit,))
        return curseur.fetchall()


def obtenir_details_service(conn, id_service):
    """Retourne les détails d’un service"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT s.id_service, s.titre, s.description, s.localisation,
                   s.date_creation, s.actif, s.cout, s.photo,
                   c.nom_categorie AS categorie
            FROM services s
            JOIN categories c ON s.id_categorie = c.id_categorie
            WHERE s.id_service = %s
        """, (id_service,))
        return curseur.fetchone()


def obtenir_categories(conn):
    """Retourne toutes les catégories"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_categorie, nom_categorie FROM categories")
        return curseur.fetchall()


def inserer_service(conn, titre, localisation, description, cout, actif, photo, categorie, id_proprietaire):
    """Ajoute un nouveau service"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO services (titre, localisation, description, cout, actif, photo, id_categorie, id_proprietaire)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (titre, localisation, description, cout, actif, photo, categorie, id_proprietaire))


def obtenir_service_par_id(conn, id_service):
    """Retourne un service par son identifiant"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT *
            FROM services s
            JOIN categories c ON s.id_categorie = c.id_categorie
            WHERE s.id_service = %s
        """, (id_service,))
        return curseur.fetchone()



def mettre_a_jour_service(conn, id_service, titre, localisation, description, cout, actif, photo):
    """Met à jour un service existant (sans changer la catégorie)"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            UPDATE services
            SET titre=%s,
                localisation=%s,
                description=%s,
                cout=%s,
                actif=%s,
                photo=%s
            WHERE id_service=%s
        """, (titre, localisation, description, cout, actif, photo, id_service))

    conn.commit()



def obtenir_tous_les_services(conn):
    """Retourne la liste complète des services"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT s.id_service, s.titre, s.description, s.localisation,
                   s.photo, s.id_proprietaire, s.actif, s.cout,
                   c.nom_categorie
            FROM services s
            JOIN categories c ON s.id_categorie = c.id_categorie
            ORDER BY s.date_creation DESC
        """)
        return curseur.fetchall()


def supprimer_service(conn, id_service, id_proprietaire):
    """Supprime un service appartenant à un utilisateur, s’il n’est pas réservé"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            DELETE FROM services
            WHERE id_service = %s
              AND id_proprietaire = %s
              AND id_service NOT IN (SELECT id_service FROM reservations)
        """, (id_service, id_proprietaire))
        conn.commit()
        return curseur.rowcount > 0



def ajouter_reservation(conn, id_utilisateur, id_service, date_heure_reservation):
    """Ajoute une réservation dans la BD"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            INSERT INTO reservations (id_utilisateur, id_service, date_heure_reservation)
            VALUES (%s, %s, %s)
        """, (id_utilisateur, id_service, date_heure_reservation))


def verifier_disponibilite(conn, id_service, date_heure_reservation):
    """Vérifie si un créneau est libre pour un service"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT COUNT(*) AS total
            FROM reservations
            WHERE id_service = %s AND date_heure_reservation = %s
        """, (id_service, date_heure_reservation))
        return curseur.fetchone()["total"] == 0

def obtenir_utilisateur_par_id(conn, id_utilisateur):
    """Retourne les infos d’un utilisateur selon son ID"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * FROM utilisateurs WHERE id_utilisateur = %s", (id_utilisateur,))
        return curseur.fetchone()


def obtenir_credit_utilisateur(conn, id_utilisateur):
    """Retourne le crédit actuel d'un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT credit FROM utilisateurs WHERE id_utilisateur = %s", (id_utilisateur,))
        resultat = curseur.fetchone()
        return resultat["credit"] if resultat else 0

def mettre_a_jour_credits(conn, id_client, id_proprietaire, cout_service):
    """Met à jour les crédits après une réservation"""
    with conn.get_curseur() as curseur:
        curseur.execute("UPDATE utilisateurs SET credit = credit - %s WHERE id_utilisateur = %s",
                        (cout_service, id_client))
        curseur.execute("UPDATE utilisateurs SET credit = credit + %s WHERE id_utilisateur = %s",
                        (cout_service, id_proprietaire))
        
def donner_credit_pour_ajout_service(conn, id_utilisateur, montant=20):
    """Donne du crédit à un utilisateur pour l'ajout d'un service"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "UPDATE utilisateurs SET credit = credit + %s WHERE id_utilisateur = %s",
            (montant, id_utilisateur)
        )
