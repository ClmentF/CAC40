#!/bin/bash

echo "🔄 Mise à jour des données CAC 40"
echo "================================="

# Vérifier que les conteneurs sont démarrés
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Les conteneurs ne sont pas démarrés. Lancement..."
    docker-compose up -d
    sleep 10
fi

# Mise à jour des données
echo "📊 Téléchargement des dernières données..."
docker-compose exec -T app python /app/load_data.py

echo ""
echo "✅ Mise à jour terminée !"
