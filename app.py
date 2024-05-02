import fuzzywuzzy
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from fuzzywuzzy import process
import csv
import data
import re
import pandas as pd
from difflib import SequenceMatcher

app = Flask(__name__)

dati_reperti = None

def split_name(name):
    """
    Removes a specific substring from the artifact name.

    Args:
        name (str): The full name of the artifact.

    Returns:
        str: The modified artifact name with 'Church Floor Artifact - ' removed.
    """
    return name.replace('Church Floor Artifact - ', '')

def trova_miglior_corrispondenza(nome_chiesa, path_file='Churches.csv'):
    """
    Finds the closest church name match from a CSV file using fuzzy matching.

    Args:
        nome_chiesa (str): The church name to match.
        path_file (str): The path to the CSV file containing church names. Defaults to 'Churches.csv'.

    Returns:
        str: The best matching church name.
    """
    with open(path_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        chiese = [row[2] for row in reader if len(row) > 2]  # Assicurati che ci siano abbastanza colonne

    # Usa fuzzywuzzy per trovare la miglior corrispondenza
    migliore, punteggio = fuzzywuzzy.process.extractOne(nome_chiesa, chiese)
    return migliore

def sub(string: str):
    """
    Replaces spaces in the string with '%20' for URL encoding.

    Args:
        string (str): The string to be formatted.

    Returns:
        str: The URL-encoded string.
    """
    return string.replace(' ', '%20')


def seperator(dataDict):
    """
    Extracts specific keys from a dictionary and handles missing keys gracefully.

    Args:
        dataDict (dict): The dictionary containing artifact data.

    Returns:
        dict: A dictionary with selected artifact details, handling missing keys by setting them to None.
    """

    try:
        outputdict = {
            "url": dataDict.get("media0_medium"),
            # Utilizziamo dataDict.get() per ottenere l'URL dell'immagine o None se non presente
            "id": dataDict["birth_certificate_birthID"],
            "inscription": dataDict["data_Transcription"]
        }
    except KeyError as e:
        # Se una delle chiavi necessarie non è presente nel dataDict, restituiamo un dizionario con valori vuoti o None
        outputdict = {
            "url": None,
            "id": dataDict.get("birth_certificate_birthID"),
            "inscription": dataDict.get("data_Transcription")
        }
    return outputdict




@app.route("/")
def search_church():
    """
    Handles the index route and processes church name queries to display matching results.

    Returns:
        Rendered template: A Flask template populated with church and related artifact data.
    """
    raw_query = request.args.get('query')
    if not raw_query:
        return render_template("index.html", message="Inserisci un termine di ricerca.")

    query = trova_miglior_corrispondenza(raw_query, 'Churches.csv')

    try:
        global dati_reperti
        dati_reperti = None
        # read the csv file and search the church with the closest name
        churches = pd.read_csv('Churches.csv')
        closest_match = churches['Local Name'].apply(lambda x: SequenceMatcher(None, x, query).ratio()).idxmax()
        church_info = churches.iloc[closest_match]

        church_data = {
            'local_name': church_info['Local Name'],
            'full_name': church_info['Full Name'],
            'year_founded': church_info['Year Founded'],
            'intro_sentence': church_info['Intro sentence'],
            'history_blurb': church_info['History Blurb'],
            'longitude': church_info['Longitude Coordinate'],
            'latitude': church_info['Latitude Coordinate'],
        }

        # it gets the data of the artifacts of the church
        artifact_info = None
        with open('Churches.csv', 'r', newline='', encoding='utf8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 2 and query in row[2]:
                    artifact_info = row[-1]
                    break

        immagini = []
        id = []
        scritte = []

        if artifact_info:
            artifact_code = sub(artifact_info)
            ck_id_list = data.getGroup(artifact_code)
            dati_reperti = data.getData(ck_id_list)

            cleanData = [seperator(value) for value in dati_reperti]
            immagini = [item['url'] for item in cleanData]
            id = [split_name(item['id'])for item in cleanData]
            scritte = [item['inscription'] for item in cleanData]

        # Pass the info church and artifact data to the templates result.html
        return render_template("result.html", church_data=church_data, reperti=id, scritte=scritte, immagini=immagini,
                               query=query)
    except Exception as e:
        print(f"Error in search_church: {str(e)}")
        return render_template("index.html", message="Errore durante il processo di ricerca.")


def formatta_nome(codice_reperto):
    """
    Formats the artifact code by appending '%20Artifacts' after the first segment split by '_'.

    Args:
        codice_reperto (str): The original artifact code.

    Returns:
        str: The formatted artifact code suitable for further processing.
    """
    uppercase_letters = codice_reperto.split('_')[0]
    # add "%20Artifacts" to the string
    result_string = uppercase_letters + "%20Artifacts"
    return result_string


@app.route("/search_reperto", methods=["GET", "POST"])
def search_reperto():
    """
    Handles the artifact search route, allowing users to query by artifact code.

    Returns:
        Rendered template: A Flask template showing detailed information about the queried artifact or an error message.
    """
    query = request.args.get('query')
    if not query:
        return render_template("index.html", message="Inserisci il codice del reperto.")

    reperto_traduz = None
    reperto_id = None
    reperto_url = '/static/noimage.jpg'
    reperto_scritte = None
    reperto_condition = None
    reperto_length = None
    reperto_material = None
    reperto_width = None
    reperto_shape = None
    reperto_type = None

    try:
        global dati_reperti
        dati_reperti = None
        artifact_code = formatta_nome(query)
        ck_id_list = data.getGroup(artifact_code)
        dati_reperti = data.getData(ck_id_list)

        for reperto in dati_reperti:
            if reperto["data_Artifact Code"] == query:
                # it handles the possibilty that there is no image
                reperto_id = reperto.get("birth_certificate_ckID", None)
                reperto_url = reperto.get("media0_medium", None)
                reperto_scritte = reperto.get("data_Transcription", None)
                reperto_traduz = reperto.get("data_Translation", None)
                reperto_condition = reperto.get("data_Condition Category", None)
                reperto_length = reperto.get("data_Length", None)
                reperto_width = reperto.get("data_Width", None)
                reperto_material = reperto.get("data_Materials", None)
                reperto_shape = reperto.get("data_Shape", None)
                reperto_type = reperto.get("data_Type of Artifact", None)
                break

        if request.method == "POST":
            reperto_traduz = request.form['NEWtranslation']
            email = request.form['emailTK']
            uid = request.form['uidTK']
            data.update_translation(reperto_id, reperto_traduz, email, uid)

        if reperto_url or reperto_scritte:  # Verifiy if we found useful data
            return render_template("clickReperto.html", reperto=query, scritte=reperto_scritte,
                                   immagini=reperto_url, traduzione=reperto_traduz, condizione=reperto_condition,
                                   length=reperto_length,
                                   width=reperto_width, material=reperto_material, shape=reperto_shape,
                                   type=reperto_type, query=query)
        else:
            return render_template("index.html", message="Nessun dato disponibile per il codice inserito.")

    except Exception as e:
        print("Errore:", e)
        return render_template("index.html",
                               message="Errore nel processo di ricerca. Assicurati che il codice del reperto sia "
                                       "valido.")



if __name__ == "__main__":
    app.run(debug=True)
