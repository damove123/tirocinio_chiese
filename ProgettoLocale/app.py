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
        codice_chiesa = request.form['codice_chiesa']

        # Lista per memorizzare le corrispondenze trovate
        corrispondenze = []

        # Apro il file JSON
        with open('/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/RepertiPolo.json', 'r') as file:
            # Carico il contenuto del file JSON in una lista di dizionari
            dati = json.load(file)

            # Cerco tutti i record con il Codice Chiesa specificato
            for record in dati:
                if record.get('Codice Chiesa') == codice_chiesa:
                    # Aggiungo il record alla lista delle corrispondenze
                    corrispondenze.append(record)

            if corrispondenze:
                # Se ci sono corrispondenze, restituisco la lista di record
                return jsonify(corrispondenze)
            else:
                # Se non ci sono corrispondenze, restituisco un messaggio
                return jsonify({'messaggio': f'Codice Chiesa "{codice_chiesa}" non trovato'})

    except Exception as e:
        # Se si verifica un'eccezione, restituisco un messaggio di errore
        return jsonify({'errore': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
