import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template, request
import pandas as pd
import csv
import data

app = Flask(__name__)

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"
})

@app.route("/")
def search_church():
    query = request.args.get('query')
    if not query:
        return render_template("index.html", message="Inserisci un termine di ricerca.")

    reperti, immagini, ids, scritte = [], [], [], []

    try:
        with open('Churches.csv', 'r', newline='', encoding='utf8') as file:
            reader = csv.reader(file)
            found = False
            for row in reader:
                if query.lower() in row[2].lower():  # Assumo che il nome della chiesa sia nella terza colonna
                    found = True
                    ck_id_list = data.getGroup(row[2])  # Assumo che il codice della chiesa sia nella stessa colonna
                    artifact_data = data.getData(ck_id_list)
                    for artifact in artifact_data:
                        parsed_data = data.seperator(artifact)
                        reperti.append(parsed_data)
                        immagini.append(parsed_data['url'])
                        ids.append(parsed_data['id'])
                        scritte.append(parsed_data['inscription'])
                    break
            if not found:
                return render_template("index.html", message="Nessun risultato trovato per: " + query)

        return render_template("result.html", chiesa=query, reperti=ids, scritte=scritte, immagini=immagini, query=query)

    except Exception as e:
        print(f"Error in search_church: {str(e)}")
        return render_template("index.html", message="Errore durante il processo di ricerca.")

if __name__ == "__main__":
    app.run(debug=True)
