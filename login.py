from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import re
from fuzzywuzzy import fuzz

import app

# Imposta una chiave segreta casuale
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
    return fuzz.ratio(query, target) > 80


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
