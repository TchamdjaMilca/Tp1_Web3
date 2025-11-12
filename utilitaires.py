from flask import abort, session

import bd
import hashlib


def hacher_mdp(mdp_clair):
    """hacher mdp"""
    return hashlib.sha512(mdp_clair.encode('utf-8')).hexdigest()

def valider_service(form, fichiers, categories):
    erreurs = {}
    titre = form.get('titre', '').strip()
    localisation = form.get('localisation', '').strip()
    description = form.get('description', '').strip()
    cout = form.get('cout', '').strip()
    photo = fichiers.get('photo')

    if not titre or len(titre) > 50:
        erreurs['titre'] = 'Titre invalide'
    if not localisation or len(localisation) > 50:
        erreurs['localisation'] = 'Localisation invalide'
    if not description or len(description) < 5:
        erreurs['description'] = 'Description invalide'
    if not cout or float(cout) < 0:
        erreurs['cout'] = 'Cout invalide'

    return erreurs, photo

