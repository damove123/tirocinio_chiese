from flask import Flask, render_template, jsonify, json, request
import csv

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


# Definire la rotta per la lettura del file JSON
@app.route('/leggi_json', methods=['POST'])
def leggi_json():
    try:
        # Leggere il Codice Chiesa immesso nel form
        nome_chiesa = request.form['nome_chiesa']
        codice_chiesa = []
        reperti_chiesa = []

        # Lista per memorizzare le corrispondenze trovate
        corrispondenze = []

        # Apro il file JSON
        with open('/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/Chiese.json', 'r') as file:
            # Carico il contenuto del file JSON in una lista di dizionari
            dati1 = json.load(file)

        with open('/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/RepertiPolo.json', 'r') as file:
            # Carico il contenuto del file JSON in una lista di dizionari
            dati2 = json.load(file)

        with open('/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/_RepertiPivi.json', 'r') as file:
            # Carico il contenuto del file JSON in una lista di dizionari
            dati3 = json.load(file)

        for chiesa in dati1:
            if chiesa.get('Locale Nome della Chiesa') == nome_chiesa:
                codice_chiesa = chiesa.get('Codice Chiesa')
                break

        for codice_da_trovare in dati2:
            if codice_da_trovare.get('Codice Chiesa') == codice_chiesa:
                reperti_chiesa.append(codice_da_trovare)

        for codice_da_trovare in dati3:
            if codice_da_trovare.get('Codice Chiesa') == codice_chiesa:
                reperti_chiesa.append(codice_da_trovare)

        if reperti_chiesa:
            return jsonify(reperti_chiesa)
        else:
            return jsonify({'messaggio': 'Nessun reperto trovato per questa chiesa'})

    except Exception as e:
        # Se si verifica un'eccezione, restituisco un messaggio di errore
        return jsonify({'errore': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
