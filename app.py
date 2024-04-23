import fuzzywuzzy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from fuzzywuzzy import fuzz, process
from flask_caching import Cache
import csv
import data
import re

app = Flask(__name__)
app.secret_key = 'Chiese2012!'  # Imposta una chiave segreta casuale

# Credenziali predefinite
USERNAME = "chiese2024@gmail.com"
PASSWORD = "pippo2001"

login_manager = LoginManager(app)
login_manager.login_view = "login"

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


# Definizione del modello utente
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# Funzione per recuperare un utente dall'ID
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def trova_miglior_corrispondenza(nome_chiesa, path_file='Churches.csv'):
    with open(path_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        chiese = [row[2] for row in reader if len(row) > 2]  # Assicurati che ci siano abbastanza colonne

    # Usa fuzzywuzzy per trovare la miglior corrispondenza
    migliore, punteggio = fuzzywuzzy.process.extractOne(nome_chiesa, chiese)
    return migliore


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or url_for('search_reperto', query=session.get('last_search', ''))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email_valido(email) and password_valida(password) and email == USERNAME and PASSWORD == password:
            user = User(id=email)
            login_user(user, remember=False)
            return redirect(next_url)
        else:
            flash('Email o password non valide', 'error')
    return render_template('login.html', next=next_url)


# Route per il logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Effettua il logout dell'utente
    return redirect(url_for('search_church'))  # Reindirizza l'utente alla homepage dopo il logout


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
    global dati_reperti
    dati_reperti = None
    # Controlla se l'utente è autenticato
    if current_user.is_authenticated:
        raw_query = request.args.get('query')
        if not raw_query:
            # Restituisce subito se non c'è una query
            return render_template("index.html", message="Inserisci un termine di ricerca.")

        query = trova_miglior_corrispondenza(raw_query)
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
            dati_reperti = data.getData(ck_id_list)

            for artifact in dati_reperti:
                reperti.append(artifact)

            cleanData = [seperator(value) for value in reperti]

            for item in cleanData:
                immagini.append(item['url'])
                id.append(item['id'])
                scritte.append(item['inscription'])

            return render_template("result.html", chiesa=query, reperti=id, scritte=scritte, immagini=immagini,
                                   query=query)

        except Exception as e:
            print(f"Error in search_church: {str(e)}")
            return render_template("index.html", message="Errore durante il processo di ricerca.")
        else:
            return redirect(url_for('login'))  # Reindirizza l'utente alla pagina di login se non è autenticato


def formatta_nome(codice_reperto):
    uppercase_letters = codice_reperto.split('_')[0]
    # Aggiunge "%20Artifacts" alla stringa di lettere maiuscole
    result_string = uppercase_letters + "%20Artifacts"
    return result_string


@app.route("/click_reperto", methods=["GET"])
@login_required
def click_reperto():
    query = request.args.get('query')
    if not query:
        return render_template("index.html", message="Inserisci il codice del reperto.")

    reperto_traduz = None
    reperto_url = None
    reperto_scritte = None
    try:
        codice_reperto = normalize_name(query)
        artifact_group = formatta_nome(codice_reperto)
        ck_id_list = data.getGroup(artifact_group)
        dati_reperti = data.getData(ck_id_list)
        for reperto in dati_reperti:
            if reperto["data_Artifact Code"] == codice_reperto:
                # Gestisce la possibilità che l'immagine non sia disponibile
                reperto_url = reperto.get("media0_medium", None)
                reperto_scritte = reperto.get("data_Transcription", None)
                reperto_traduz = reperto.get("data_Translation", None)
                break  # Esce dal ciclo una volta trovato il reperto corrispondente

        if reperto_url or reperto_scritte:  # Verifica se abbiamo trovato dati utili
            return render_template("clickReperto.html", reperto=query, scritte=reperto_scritte,
                                   immagini=reperto_url, traduzione=reperto_traduz, query=query)
        else:
            return render_template("index.html", message="Nessun dato disponibile per il codice inserito.")

    except Exception as e:
        print("Errore:", e)
        return render_template("index.html",
                               message="Errore nel processo di ricerca. Assicurati che il codice del reperto sia "
                                       "valido.")


@app.route("/search_reperto", methods=["GET"])
def search_reperto():
    query = request.args.get('query')
    session['last_search'] = query  # Salva la query nella sessione
    next_url = url_for('click_reperto', query=query)
    if current_user.is_authenticated:
        return redirect(next_url)
    else:
        return redirect(url_for('login', next=next_url))


if __name__ == "__main__":
    app.run(debug=True)
