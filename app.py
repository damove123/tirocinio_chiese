import firebase_admin
from firebase_admin import db, credentials
from flask import Flask, render_template, jsonify, request
from fuzzywuzzy import fuzz
from flask_caching import Cache
import pandas as pd
import csv
import data

import boto3

app = Flask(__name__)

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


def get_general_image_urls(bucket_name, church_code):
    extensions = ['jpg', 'JPG']
    image_urls = []
    prefix = f"Church_Photos/{church_code}/General/"

    try:
        # Recupero tutti gli oggetti che iniziano con il prefisso della cartella
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        print("Response from S3:", response)  # Stampa la risposta completa per debug

        if response['KeyCount'] > 0:
            # Filtriamo i risultati per estensione
            for item in response.get('Contents', []):
                if any(item['Key'].endswith(ext) for ext in extensions):
                    image_url = f"https://{bucket_name}.s3.amazonaws.com/{item['Key']}"
                    image_urls.append(image_url)

    except Exception as e:
        print(f"Errore nel recupero delle immagini: {e}")

    if not image_urls:
        print("Non esistono altre foto per questa chiesa.")

    return image_urls


def get_floor_image_urls(bucket_name, church_code):
    extensions = ['jpg', 'JPG']
    image_urls = []
    prefix = f"Church_Photos/{church_code}/Floor/"

    try:
        # Recupero tutti gli oggetti che iniziano con il prefisso della cartella
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        print("Response from S3:", response)  # Stampa la risposta completa per debug

        if response['KeyCount'] > 0:
            # Filtriamo i risultati per estensione
            for item in response.get('Contents', []):
                if any(item['Key'].endswith(ext) for ext in extensions):
                    image_url = f"https://{bucket_name}.s3.amazonaws.com/{item['Key']}"
                    image_urls.append(image_url)

    except Exception as e:
        print(f"Errore nel recupero delle immagini: {e}")

    if not image_urls:
        print("Non esistono foto dei pavimenti per questa chiesa.")

    return image_urls


cache = Cache(app, config={'CACHE_TYPE': 'simple'})


def sub(string: str):
    return string.replace(' ', '%20')


def seperator(dataDict):
    try:
        outputdict = {
            "url": dataDict.get("media0_medium"),  # Utilizziamo dataDict.get() per ottenere l'URL dell'immagine o None se non presente
            "id": dataDict["birth_certificate_birthID"],
            "inscription": dataDict["data_Inscription"]
        }
    except KeyError as e:
        # Se una delle chiavi necessarie non è presente nel dataDict, restituiamo un dizionario con valori vuoti o None
        outputdict = {
            "url": None,
            "id": dataDict.get("birth_certificate_birthID"),
            "inscription": dataDict.get("data_Inscription")
        }
    return outputdict



@app.route("/")
def search_church():
    raw_query = request.args.get('query')
    if not raw_query:
        # Restituisce subito se non c'è una query
        return render_template("index.html", message="Inserisci un termine di ricerca.")

    query = normalize_name(raw_query)
    reperti = []
    immagini = []
    id = []
    scritte = []

    try:
        artifact_info = None
        with open('Churches.csv', 'r', newline='', encoding='utf8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 2 and query in row[2]:
                    artifact_info = row[-1]
                    break

        if artifact_info is None:
            # Nessun risultato trovato nel CSV
            return render_template("index.html", message=f"Nessun risultato trovato per: {query}")

        artifact_code = sub(artifact_info)
        ck_id_list = data.getGroup(artifact_code)
        artifact_url = data.getData(ck_id_list)
        for artifact in artifact_url:
            reperti.append(artifact)

        cleanData = [seperator(value) for value in reperti]

        for item in cleanData:
            immagini.append(item['url'])
            id.append(item['id'])
            scritte.append(item['inscription'])

        return render_template("result.html", chiesa=query, reperti=id, scritte=scritte, immagini=immagini, query=query)

    except Exception as e:
        print(f"Error in search_church: {str(e)}")
        return render_template("index.html", message="Errore durante il processo di ricerca.")


if __name__ == "__main__":
    app.run(debug=True)