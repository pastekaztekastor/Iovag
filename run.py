"""
Point d'entrée de l'application Iovag
"""
from app import create_app
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Mode développement uniquement (utilisez Gunicorn en production)
    app.run(debug=True, host='0.0.0.0', port=5000)

# Pour Gunicorn : l'objet 'app' est directement accessible
