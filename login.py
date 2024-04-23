from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

app = Flask(__name__)
app.secret_key = 'una_chiave_segreto_molto_sicura'  # Imposta una chiave segreta per le sessioni

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Credenziali predefinite
USERNAME = 'utente'
PASSWORD = 'passwordsegreta'



# Definizione dell'utente
class User(UserMixin):
    def __init__(self, id):
        self.id = id


# Caricamento dell'utente
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            user = User(id=username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Nome utente o password non validi.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return 'Benvenuto nel Dashboard!'
