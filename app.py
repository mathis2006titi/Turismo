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
# SUPPRESSION TEMPORAIRE D'UN FICHIER
# ------------------------------
@app.route('/delete/<filename>')
def delete(filename):
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"{filename} a été supprimé avec succès.")
    else:
        flash("Fichier non trouvé.")
    return redirect(url_for('index'))

import smtplib
from email.message import EmailMessage
from flask import request, flash, redirect, url_for

@app.route('/send_email', methods=['POST'])
def send_email():
    recipient = request.form['email']
    
    # Création du message
    msg = EmailMessage()
    msg['Subject'] = "Mes informations de contact"
    msg['From'] = os.environ.get("cocotte3euros@gmail.com")  # ton email Gmail
    msg['To'] = recipient
    msg.set_content("Bonjour,\n\nVeuillez trouver en pièce jointe mon CV et ma lettre de motivation.\n\nCordialement,\nMathis Durand Cullerier")
    
    # Pièces jointes
    for filename in ['CV_Mathis_DURAND_CULLERIER.pdf', 'Lettre_Motivation.pdf']:
        path = os.path.join('static/docs', filename)
        with open(path, 'rb') as f:
            file_data = f.read()
            file_name = filename
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
    
    # Envoi via Gmail SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.environ.get("EMAIL_ADDRESS"), os.environ.get("EMAIL_PASSWORD"))
            smtp.send_message(msg)
        flash("Email envoyé avec succès ! Vérifiez votre boîte de réception.")
    except Exception as e:
        flash(f"Erreur lors de l'envoi de l'email : {e}")
    
    return redirect(url_for('index'))


# ------------------------------
# Lancement serveur local
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
