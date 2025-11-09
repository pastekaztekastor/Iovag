#!/bin/bash
# Configuration de DuckDNS pour iovag.duckdns.org

DOMAIN="iovag"
TOKEN="3c79ff91-9fa8-49c9-92bc-3270ded9a108"

echo "=========================================="
echo "Configuration de DuckDNS"
echo "=========================================="

# Créer le dossier duckdns
mkdir -p ~/duckdns
cd ~/duckdns

# Créer le script de mise à jour
cat > duck.sh << EOF
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod 700 duck.sh

# Tester le script
echo "🧪 Test de la mise à jour DuckDNS..."
./duck.sh

# Vérifier le résultat
if grep -q "OK" duck.log; then
    echo "✅ DuckDNS configuré avec succès !"
    echo "📝 Ton domaine: iovag.duckdns.org"
else
    echo "❌ Erreur lors de la configuration DuckDNS"
    cat duck.log
    exit 1
fi

# Ajouter au crontab pour mise à jour automatique toutes les 5 minutes
echo "⏰ Configuration de la mise à jour automatique..."
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1") | crontab -

echo ""
echo "✅ Configuration terminée !"
echo "DuckDNS mettra à jour ton IP automatiquement toutes les 5 minutes"
