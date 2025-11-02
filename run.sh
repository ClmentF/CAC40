#!/bin/bash

echo "🚀 Lancement de l'application CAC 40"
echo "====================================="

# Vérification que les conteneurs sont démarrés
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Les conteneurs ne sont pas démarrés. Lancement..."
    docker-compose up -d
    sleep 5
fi

# Démarrage de l'API FastAPI en arrière-plan
echo "🔌 Démarrage de l'API FastAPI..."
docker-compose exec -d app uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Attente que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 3

# Démarrage de Streamlit
echo "🎨 Lancement de l'interface Streamlit..."
docker-compose exec app streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

echo ""
echo "✅ Application lancée !"
