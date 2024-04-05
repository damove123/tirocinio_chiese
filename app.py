import firebase_admin
import json
import flask

from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"})

app = Flask(__name__)




@app.route("/")
def homepage():
    try:
        ref = db.reference("/Chiese")
        chiese = ref.get()
        if chiese:
            return render_template("index.html", chiese=chiese)
        else:
            return render_template("index.html", chiese=None)
    except Exception as e:
        app.logger.error(f"Errore durante il recupero dei dati: {e}")
        return jsonify({'error': 'Impossibile completare la richiesta'}), 500


if __name__ == "__main__":
    app.run(debug=True)
