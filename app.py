import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from werkzeug.utils import secure_filename

# ------------------------------
# Config
# ------------------------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg', 'mp4', 'mov'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SECRET_KEY sécurisé pour Render via variable d'environnement
app.secret_key = os.environ.get("SECRET_KEY", "change_this_secret_key")

# Création du dossier d'uploads si inexistant
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------------------
# Fonction utilitaire pour vérifier les fichiers autorisés
# ------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# ------------------------------
# Page de login avant accès
# ------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')

        if password == "Turismo":  # mot de passe obligatoire
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            flash("Mot de passe incorrect.")
            return redirect(url_for('login'))

    return render_template('login.html')

# ------------------------------
# Page d'accueil protégée
# ------------------------------
@app.route('/', methods=['GET'])
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    pdfs = [f for f in files if f.lower().endswith('pdf')]
    images = [f for f in files if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    videos = [f for f in files if f.lower().endswith(('mp4', 'mov'))]
    first_video = videos[0] if videos else None

    return render_template('index.html', pdfs=pdfs, images=images, video=first_video)

# ------------------------------
# Upload de fichiers
# ------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('Aucun fichier envoyé.')
        return redirect(url_for('index'))
    
    file = request.files['file']

    if file.filename == '':
        flash('Aucun fichier sélectionné.')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Fichier chargé avec succès.')
    else:
        flash('Type de fichier non autorisé.')

    return redirect(url_for('index'))

# ------------------------------
# Téléchargement des fichiers
# ------------------------------
@app.route('/download/<filename>')
def download(filename):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ------------------------------
# Lancement serveur local
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
