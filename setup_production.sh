#!/bin/bash
# Script d'installation pour production avec DuckDNS + Nginx + Gunicorn + Certbot

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "Installation des composants de production"
echo "=========================================="

# 1. Mise à jour du système
echo "📦 Mise à jour du système..."
sudo apt update
sudo apt upgrade -y

# 2. Installation de Nginx
echo "📦 Installation de Nginx..."
sudo apt install -y nginx

# 3. Installation de Certbot pour HTTPS
echo "📦 Installation de Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# 4. Installation de Gunicorn (serveur WSGI Python)
echo "📦 Installation de Gunicorn..."
cd ~/iovag
source venv/bin/activate
pip install gunicorn

# 5. Installation de curl pour DuckDNS
echo "📦 Installation de curl..."
sudo apt install -y curl

# 6. Arrêter Flask si il tourne
echo "🛑 Arrêt de Flask dev server..."
pkill -f "flask run" || echo "Flask n'était pas lancé"

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Prochaines étapes :"
echo "1. Configurer DuckDNS avec ton token"
echo "2. Configurer Nginx"
echo "3. Obtenir le certificat HTTPS"
echo "4. Démarrer Gunicorn"
