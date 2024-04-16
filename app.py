import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify, request
from fuzzywuzzy import fuzz
import boto3

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"
})

# Configura il client S3
s3_client = boto3.client('s3')


def normalize_name(name):
    if not name:
        return ""  # Restituisci una stringa vuota se il nome è None o vuoto
    name = name.replace("S.", "San").replace("St.", "Santo")
    return name.strip()


def is_match(query, target):
    # Utilizza una soglia per determinare se considerare un match valido
    return fuzz.ratio(query, target) > 80  # ad esempio, una soglia del 80%


def get_image_urls(bucket_name, church_code, reperto_code):

    extensions = ['jpg', 'JPG']
    # Il prefisso ora include anche il nome del file immagine specifico per il reperto.
    for extension in extensions:
        prefix = f"Church_Photos/{church_code}/Artifacts/{reperto_code}.{extension}"
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            print("Response from S3:", response)  # Stampa la risposta completa per debug
            if response['KeyCount'] == 0:
                print(f"Nessun oggetto trovato con il prefisso {prefix}")
            else:
                # Poiché ci aspettiamo un solo file, prendiamo direttamente il primo risultato.
                image_url = f"https://{bucket_name}.s3.amazonaws.com/{response['Contents'][0]['Key']}"
                return [image_url]
        except Exception as e:
            print(f"Errore nel recupero delle immagini: {e}")
    return []


app = Flask(__name__)


@app.route("/")
def search_church():
    try:
        raw_query = request.args.get('query')
        query = normalize_name(raw_query)
        codice_corrispondente = None
        chiese_ref = db.reference("/Chiese")
        chiese = chiese_ref.get() or []

        for chiesa in chiese:
            chiesa_name = normalize_name(chiesa.get("Locale Nome della Chiesa"))
            if is_match(query, chiesa_name):
                codice_corrispondente = chiesa.get("Codice Chiesa")
                break

        resultsChiese = []
        resultsReperti = []
        if codice_corrispondente:
            resultsChiese.extend([chiesa for chiesa in chiese if chiesa.get("Codice Chiesa") == codice_corrispondente])

            refPivi = db.reference("/RepertiPivi").get() or []
            for pivi in refPivi:
                if pivi.get("Codice Chiesa") == codice_corrispondente:
                    pivi['image_urls'] = get_image_urls('floor-tiles-vpc', codice_corrispondente,
                                                        pivi.get("Codice Reperto"))
                    resultsReperti.append(pivi)

            refPolo = db.reference("/RepertiPolo").get() or []
            for polo in refPolo:
                if polo.get("Codice Chiesa") == codice_corrispondente:
                    polo['image_urls'] = get_image_urls('floor-tiles-vpc', codice_corrispondente,
                                                        polo.get("Codice Reperto"))
                    resultsReperti.append(polo)

        if resultsChiese:
            return render_template("result.html", chiese=resultsChiese, reperti=resultsReperti, query=query)
        else:
            return render_template("index.html", chiese=None, reperti=None, query=query)
    except Exception as e:
        print("Errore durante la ricerca:", str(e))  # Aggiunge dettaglio sull'errore
        return jsonify({'error': 'Impossibile completare la ricerca: ' + str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

#vZhB/X2+X7V+Sgk17/cLvO7QuQMf5Uy+nS2Hue6k