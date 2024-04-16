import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify, request

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"
})

app = Flask(__name__)

'''
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
'''
'''
@app.route("/search")
def search():
    query = request.args.get("query")
    if query:
        try:
            ref = db.reference("/Chiese")
            chiese = ref.get()
            if chiese:
                filtered_chiese = [chiesa for chiesa in chiese if query.lower() in chiesa.get("Nome Locale della Chiesa", "").lower()]
                return render_template("index.html", chiese=filtered_chiese, query=query)
            else:
                return render_template("index.html", chiese=None, query=query)
        except Exception as e:
            app.logger.error(f"Errore durante la ricerca delle chiese: {e}")
            return jsonify({'error': 'Impossibile completare la ricerca'}), 500
    else:
        return render_template("index.html", chiese=None, query="")
'''
@app.route("/")
def search_church():
    try:
        query = request.args.get('query').lower()  # Ottieni il valore inserito nell'input di ricerca
        ref = db.reference("/Chiese")
        chiese = ref.get()

        # Filtra le chiese che corrispondono alla query
        results = [chiesa for chiesa in chiese if chiesa["Locale Nome della Chiesa"] == query]


        if results:
            return render_template("index.html", chiese=results, query=query)
        else:
            return render_template("index.html", chiese=None, query=query)
    except Exception as e:
        app.logger.error(f"Errore durante la ricerca della chiesa: {e}")
        return jsonify({'error': 'Impossibile completare la ricerca'}), 500





if __name__ == "__main__":
    app.run(debug=True)
