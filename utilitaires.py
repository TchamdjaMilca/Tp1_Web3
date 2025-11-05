from flask import abort, session

import bd
import hashlib


def hacher_mdp(mdp_clair):
    """hacher mdp"""
    return hashlib.sha512(mdp_clair.encode('utf-8')).hexdigest()


