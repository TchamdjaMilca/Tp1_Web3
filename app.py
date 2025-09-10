"""
Pour démontrer l'utilisation des templates
"""

import random

from flask import Flask, render_template    
import bd

app = Flask(__name__)


@app.route('/')
def index():
    """Page d'index"""
    try:
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                curseur.execute('SELECT * FROM services ')
                service = curseur.fetchall()
                print(service)
        return render_template('index.jinja', service=service)
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return "Erreur de connexion à la base de données"


if __name__ == '__main__':
    app.run(debug=True)
