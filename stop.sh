#!/bin/bash

echo "🛑 Arrêt de l'application CAC 40"
echo "================================="

echo "Arrêt des services..."
docker-compose down

echo ""
echo "✅ Application arrêtée"
echo ""
echo "Pour redémarrer : ./run.sh"
echo "Pour supprimer les données : docker-compose down -v"
