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


# Funzione per validare l'email
def email_valido(email):
    # Utilizza un'espressione regolare per controllare il formato dell'email Questo pattern corrisponde a un'email
    # standard, ma potrebbe essere necessario adattarlo alle tue esigenze specifiche
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# Funzione per validare la password
def password_valida(password):
    # Controlla se la password ha almeno 8 caratteri
    return len(password) >= 8


def trova_miglior_corrispondenza(nome_chiesa, path_file='Churches.csv'):
    with open(path_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        chiese = [row[2] for row in reader if len(row) > 2]  # Assicurati che ci siano abbastanza colonne

    # Usa fuzzywuzzy per trovare la miglior corrispondenza
    migliore, punteggio = fuzzywuzzy.process.extractOne(nome_chiesa, chiese)
    return migliore


def sub(string: str):
    return string.replace(' ', '%20')


def seperator(dataDict):
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
    raw_query = request.args.get('query')
    if not raw_query:
        return render_template("index.html", message="Inserisci un termine di ricerca.")

    query = trova_miglior_corrispondenza(raw_query, 'Churches.csv')

    try:
        global dati_reperti
        dati_reperti = None
        # Legge il file CSV e cerca la chiesa con il nome più simile alla query
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

        # Estrae i dati necessari dai reperti correlati alla chiesa trovata
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
            id = [item['id'] for item in cleanData]
            scritte = [item['inscription'] for item in cleanData]

        # Passa le informazioni della chiesa e i dati dei reperti al template
        return render_template("result.html", church_data=church_data, reperti=id, scritte=scritte, immagini=immagini, query=query)
    except Exception as e:
        print(f"Error in search_church: {str(e)}")
        return render_template("index.html", message="Errore durante il processo di ricerca.")


def formatta_nome(codice_reperto):
    uppercase_letters = codice_reperto.split('_')[0]
    # Aggiunge "%20Artifacts" alla stringa di lettere maiuscole
    result_string = uppercase_letters + "%20Artifacts"
    return result_string


@app.route("/search_reperto", methods=["GET", "POST"])
def search_reperto():
    query = request.args.get('query')
    if not query:
        return render_template("index.html", message="Inserisci il codice del reperto.")

    reperto_traduz = None
    reperto_id = None
    reperto_url = None
    reperto_scritte = None
    reperto_condition = None
    reperto_length = None
    reperto_material = None
    reperto_width = None
    reperto_shape = None
    reperto_type = None

    try:
        global dati_reperti
        if dati_reperti is None:
            artifact_code = formatta_nome(query)
            ck_id_list = data.getGroup(artifact_code)
            dati_reperti = data.getData(ck_id_list)

        for reperto in dati_reperti:
            if reperto["data_Artifact Code"] == query:
                # Gestisce la possibilità che l'immagine non sia disponibile
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
                break  # Esce dal ciclo una volta trovato il reperto corrispondente

        if request.method == "POST":
                    reperto_traduz = request.form['NEWtranslation']
                    email = request.form['emailTK']
                    uid = request.form['uidTK']
                    data.update_translation(reperto_id, reperto_traduz,email,uid)

        if reperto_url or reperto_scritte:  # Verifica se abbiamo trovato dati utili
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


@app.route('/search')
def search():
    church_name = request.args.get('chiesa', '')
    churches = pd.read_csv('Churches.csv')
    # Utilizza SequenceMatcher per trovare il nome più simile
    closest_match = churches['Local Name'].apply(lambda x: SequenceMatcher(None, x, church_name).ratio()).idxmax()
    church_info = churches.iloc[closest_match]
    return render_template('results.html', church_info=church_info)


if __name__ == "__main__":
    app.run(debug=True)
