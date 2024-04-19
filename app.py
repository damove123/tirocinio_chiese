from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from fuzzywuzzy import fuzz
from flask_caching import Cache
import csv
import data
import re

app = Flask(__name__)
app.secret_key = 'Chiese2012!'  # Imposta una chiave segreta casuale
login_manager = LoginManager(app)


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

# Definizione del modello utente
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# Funzione per recuperare un utente dall'ID
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# Normalizza il nome
def normalize_name(name):
    if not name:
        return ""  # Restituisci una stringa vuota se il nome è None o vuoto
    name = name.replace("S.", "San").replace("St.", "Santo")
    return name.strip()


# Verifica se c'è una corrispondenza tra la query e il target
def is_match(query, target):
    # Utilizza una soglia per determinare se considerare un match valido
    return fuzz.ratio(query, target) > 80  # ad esempio, una soglia del 80%


# Route per il login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Esegui la logica di autenticazione qui
        if email_valido(email) and password_valida(password):
            user = User(id=email)  # Crea un oggetto utente
            login_user(user)  # Effettua il login dell'utente
            return redirect(url_for('search_church'))  # Reindirizza l'utente dopo il login
        else:
            flash('Email o password non valide', 'error')
    return render_template('login.html')


# Route per il logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Effettua il logout dell'utente
    return redirect(url_for('search_church'))  # Reindirizza l'utente alla homepage dopo il logout


cache = Cache(app, config={'CACHE_TYPE': 'simple'})


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
    # Controlla se l'utente è autenticato
    if current_user.is_authenticated:
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
    else:
        return redirect(url_for('login'))  # Reindirizza l'utente alla pagina di login se non è autenticato

if __name__ == "__main__":
    app.run(debug=True)
