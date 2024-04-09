import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify, request

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"
})

app = Flask(__name__)


@app.route("/")
def search_church():
    try:
        query = request.args.get('query')  # Ottieni il valore inserito nell'input di ricerca
        codice_corrispondente = None
        chiese_ref = db.reference("/Chiese")
        chiese = chiese_ref.get() or []

        for chiesa in chiese:
            if chiesa.get("Locale Nome della Chiesa") == query:
                codice_corrispondente = chiesa.get("Codice Chiesa")
                break

        # Se il codice è stato trovato, procedi con il filtraggio basato su quel codice
        resultsChiese = []
        resultsReperti = []
        if codice_corrispondente:
            if chiese:  # Reuse chiese se è già popolato e non None
                resultsChiese.extend([chiesa for chiesa in chiese if chiesa.get("Codice Chiesa") == codice_corrispondente])

            refPivi = db.reference("/RepertiPivi").get() or []
            resultsReperti.extend([pivi for pivi in refPivi if pivi.get("Codice Chiesa") == codice_corrispondente])

            refPolo = db.reference("/RepertiPolo").get() or []
            resultsReperti.extend([polo for polo in refPolo if polo.get("Codice Chiesa") == codice_corrispondente])

        # Verifica se ci sono risultati prima di restituirli
        if resultsChiese:
            return render_template("index.html", chiese=resultsChiese, reperti=resultsReperti,  query=query)
        else:
            return render_template("index.html", chiese=None, reperti=None, query=query)
    except Exception as e:
        app.logger.error(f"Errore durante la ricerca: {e}")
        return jsonify({'error': 'Impossibile completare la ricerca'}), 500



if __name__ == "__main__":
    app.run(debug=True)