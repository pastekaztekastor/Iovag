#!/bin/bash
# Script de mise à jour du déploiement Iovag sur Raspberry Pi
# À exécuter sur le Pi après un git pull

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "🚀 Mise à jour Iovag Production"
echo "=========================================="

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "run.py" ]; then
    echo -e "${RED}❌ Erreur: run.py non trouvé. Êtes-vous dans le bon répertoire ?${NC}"
    exit 1
fi

echo -e "${YELLOW}📍 Répertoire actuel: $(pwd)${NC}"

# 1. Arrêter le service
echo ""
echo -e "${YELLOW}1️⃣ Arrêt du service en cours...${NC}"
if pgrep -f gunicorn > /dev/null; then
    echo "   Arrêt de Gunicorn..."
    pkill -f gunicorn || true
    sleep 2
    echo -e "${GREEN}   ✅ Gunicorn arrêté${NC}"
else
    echo "   ℹ️  Gunicorn n'était pas en cours d'exécution"
fi

# 2. Git pull
echo ""
echo -e "${YELLOW}2️⃣ Récupération des derniers changements...${NC}"
git fetch origin
git pull origin main
echo -e "${GREEN}   ✅ Code mis à jour${NC}"

# 3. Activer venv et installer dépendances
echo ""
echo -e "${YELLOW}3️⃣ Installation des dépendances...${NC}"
source venv/bin/activate
pip install -q reportlab
echo -e "${GREEN}   ✅ Dépendances installées${NC}"

# 4. Migrations de base de données
echo ""
echo -e "${YELLOW}4️⃣ Exécution des migrations...${NC}"
export FLASK_APP=run.py
flask db upgrade
echo -e "${GREEN}   ✅ Migrations appliquées${NC}"

# 5. Initialiser les unités (skip si déjà fait)
echo ""
echo -e "${YELLOW}5️⃣ Initialisation des unités...${NC}"
if [ -f "init_unites.py" ]; then
    # Vérifier si les unités existent déjà
    python -c "from app import create_app, db; from app.models import Unite; app = create_app();
with app.app_context():
    count = Unite.query.count()
    print(f'Unités existantes: {count}')
    if count == 0:
        print('Initialisation des unités...')
        exec(open('init_unites.py').read())
    else:
        print('Unités déjà initialisées, skip.')
" 2>&1 | grep -v "WARNING"
    echo -e "${GREEN}   ✅ Unités vérifiées${NC}"
else
    echo -e "${YELLOW}   ⚠️  init_unites.py non trouvé, skip${NC}"
fi

# 6. Redémarrer le service
echo ""
echo -e "${YELLOW}6️⃣ Redémarrage du service...${NC}"

# Vérifier si c'est un service systemd ou gunicorn direct
if systemctl list-units --type=service | grep -q iovag; then
    echo "   Redémarrage via systemd..."
    sudo systemctl restart iovag
    sudo systemctl status iovag --no-pager -l
else
    echo "   Démarrage de Gunicorn en arrière-plan..."
    nohup gunicorn --config gunicorn_config.py run:app > /tmp/iovag_gunicorn.log 2>&1 &
    sleep 2
    if pgrep -f gunicorn > /dev/null; then
        echo -e "${GREEN}   ✅ Gunicorn démarré (PID: $(pgrep -f gunicorn | head -1))${NC}"
    else
        echo -e "${RED}   ❌ Erreur au démarrage de Gunicorn${NC}"
        echo "   Voir les logs: tail -f /tmp/iovag_gunicorn.log"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Mise à jour terminée avec succès !"
echo "==========================================${NC}"
echo ""
echo "📊 Vérifications:"
echo "   - Processus: $(pgrep -a gunicorn | head -1)"
echo "   - Site accessible: https://iovag.duckdns.org:18443"
echo ""
