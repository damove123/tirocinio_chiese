import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify, request
import boto3

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app/"
})

# Configura il client S3
s3_client = boto3.client('s3')


def get_image_urls(bucket_name, church_code, reperto_code):
    # Il prefisso ora include anche il nome del file immagine specifico per il reperto.
    prefix = f"Church_Photos/{church_code}/Artifacts/{reperto_code}.JPG"
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
        query = request.args.get('query')
        codice_corrispondente = None
        chiese_ref = db.reference("/Chiese")
        chiese = chiese_ref.get() or []

        for chiesa in chiese:
            if chiesa.get("Locale Nome della Chiesa") == query:
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
            return render_template("index.html", chiese=resultsChiese, reperti=resultsReperti, query=query)
        else:
            return render_template("index.html", chiese=None, reperti=None, query=query)
    except Exception as e:
        return jsonify({'error': 'Impossibile completare la ricerca'}), 500


if __name__ == "__main__":
    app.run(debug=True)
