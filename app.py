import firebase_admin
import json
import flask

from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"})

app = Flask(__name__)

#ref = db.reference("/Chiese").get()
#formatted_ref = json.dumps(ref, indent=4, ensure_ascii=False)
#print(formatted_ref)


@app.route("/")
def homepage():
    ref = db.reference("/Chiese").get()
    return render_template('index.html', chiese=ref)

if __name__ == "__main__":
    app.run()
