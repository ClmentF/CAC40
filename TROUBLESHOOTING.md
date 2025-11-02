# 🔧 Guide de dépannage

## Problèmes courants et solutions

### 1. Installation

#### ❌ Erreur : "Cannot connect to the Docker daemon"

**Cause** : Docker n'est pas démarré ou pas installé

**Solution** :
```bash
# Vérifier si Docker est installé
docker --version

# Démarrer Docker (Linux)
sudo systemctl start docker

# Démarrer Docker (macOS/Windows)
# Ouvrir Docker Desktop

# Vérifier le statut
docker ps
```

#### ❌ Erreur : "port is already allocated"

**Cause** : Un des ports (5432, 8000, 8501) est déjà utilisé

**Solution** :
```bash
# Identifier le processus utilisant le port
sudo lsof -i :5432
sudo lsof -i :8000
sudo lsof -i :8501

# Option 1 : Arrêter le processus
kill -9 <PID>

# Option 2 : Modifier les ports dans docker-compose.yml
# Changer "8000:8000" en "8080:8000" par exemple
```

#### ❌ Erreur : "no space left on device"

**Cause** : Espace disque insuffisant

**Solution** :
```bash
# Nettoyer les images Docker inutilisées
docker system prune -a

# Vérifier l'espace
docker system df

# Supprimer les volumes non utilisés
docker volume prune
```

### 2. Base de données

#### ❌ Erreur : "database connection refused"

**Cause** : PostgreSQL n'est pas démarré ou pas prêt

**Solution** :
```bash
# Vérifier le statut des conteneurs
docker-compose ps

# Voir les logs de PostgreSQL
docker-compose logs postgres

# Redémarrer PostgreSQL
docker-compose restart postgres

# Attendre quelques secondes puis réessayer
sleep 10
```

#### ❌ Erreur : "password authentication failed"

**Cause** : Mauvais identifiants

**Solution** :
```bash
# Vérifier les variables d'environnement dans docker-compose.yml
# Par défaut :
# POSTGRES_USER: cac40_user
# POSTGRES_PASSWORD: cac40_password

# Réinitialiser complètement
docker-compose down -v
./install.sh
```

#### ❌ Les tables sont vides

**Cause** : Données non chargées

**Solution** :
```bash
# Recharger les données
./update_data.sh

# Ou manuellement
docker-compose exec app python /app/load_data.py

# Vérifier dans la base
docker-compose exec postgres psql -U cac40_user -d cac40_db
\dt
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM stock_prices;
```

### 3. API

#### ❌ Erreur : "Connection refused" lors d'appel API

**Cause** : L'API n'est pas démarrée

**Solution** :
```bash
# Vérifier si l'API tourne
curl http://localhost:8000/health

# Voir les logs
docker-compose logs app

# Redémarrer l'API
docker-compose exec app pkill uvicorn
docker-compose exec -d app uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

#### ❌ Erreur 404 sur les endpoints

**Cause** : Mauvais chemin ou ticker invalide

**Solution** :
```bash
# Vérifier la documentation
curl http://localhost:8000/docs

# Lister les tickers disponibles
curl http://localhost:8000/companies

# Utiliser le bon format de ticker (ex: MC.PA, pas juste MC)
```

#### ❌ Erreur : "Internal Server Error" (500)

**Cause** : Erreur dans le code de l'API

**Solution** :
```bash
# Voir les logs détaillés
docker-compose logs app --tail=50

# Vérifier la connexion à la DB
curl http://localhost:8000/health

# Redémarrer l'application
docker-compose restart app
```

### 4. Streamlit

#### ❌ Page blanche ou erreur de connexion

**Cause** : Streamlit n'est pas démarré ou erreur de connexion à l'API

**Solution** :
```bash
# Vérifier si Streamlit tourne
docker-compose exec app ps aux | grep streamlit

# Voir les logs
docker-compose logs app

# Relancer Streamlit
docker-compose exec app pkill streamlit
docker-compose exec -d app streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

#### ❌ Erreur : "Connection to API failed"

**Cause** : L'API n'est pas accessible depuis Streamlit

**Solution** :
```bash
# Dans streamlit_app.py, vérifier l'URL de l'API
# Elle doit être "http://localhost:8000" si vous accédez depuis le navigateur
# Ou utiliser le nom du service si depuis le conteneur

# Tester la connexion
curl http://localhost:8000/health
```

#### ❌ Les graphiques ne s'affichent pas

**Cause** : Erreur dans les données ou problème de bibliothèque

**Solution** :
```bash
# Vérifier les logs Streamlit dans le terminal
# Rafraîchir la page (Ctrl+R)
# Vider le cache Streamlit (bouton dans le menu)

# Réinstaller les dépendances
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 5. Données yfinance

#### ❌ Erreur : "No data found for ticker"

**Cause** : Ticker invalide ou données non disponibles

**Solution** :
```python
# Vérifier manuellement avec yfinance
import yfinance as yf
ticker = yf.Ticker("MC.PA")
hist = ticker.history(period="1mo")
print(hist)

# Si vide, vérifier le ticker sur Yahoo Finance
# https://finance.yahoo.com/
```

#### ❌ Téléchargement très lent

**Cause** : Limite de taux Yahoo Finance

**Solution** :
```bash
# Ajouter des pauses dans load_data.py
# Réduire le nombre d'entreprises
# Charger les données par lots

# Modifier load_data.py pour ajouter un délai :
import time
time.sleep(1)  # Entre chaque ticker
```

#### ❌ Données manquantes ou incomplètes

**Cause** : Weekend, jours fériés, ou problème de connexion

**Solution** :
```bash
# Réessayer plus tard
./update_data.sh

# Vérifier la connexion internet
ping yahoo.com

# Augmenter la période de récupération dans load_data.py
# Changer timedelta(days=730) en timedelta(days=1095) par exemple
```

### 6. Docker

#### ❌ Conteneurs qui s'arrêtent tout seuls

**Cause** : Erreur dans l'application ou manque de ressources

**Solution** :
```bash
# Voir les logs pour identifier l'erreur
docker-compose logs --tail=100

# Vérifier les ressources système
docker stats

# Augmenter les ressources Docker (dans Docker Desktop)
# Settings > Resources > Memory (min 4GB recommandé)
```

#### ❌ Erreur : "network not found"

**Cause** : Réseau Docker corrompu

**Solution** :
```bash
# Recréer les réseaux
docker-compose down
docker network prune
docker-compose up -d
```

#### ❌ Les volumes ne persistent pas

**Cause** : Volumes supprimés par erreur

**Solution** :
```bash
# Lister les volumes
docker volume ls

# Le volume postgres_data doit exister
# Si absent, relancer l'installation
./install.sh

# NE PAS utiliser "docker-compose down -v" sauf si vous voulez tout supprimer
```

### 7. Permissions

#### ❌ Erreur : "Permission denied"

**Cause** : Problème de permissions sur les scripts

**Solution** :
```bash
# Donner les permissions d'exécution
chmod +x install.sh run.sh stop.sh update_data.sh

# Pour tous les scripts
chmod +x *.sh
```

#### ❌ Erreur d'accès aux fichiers

**Cause** : Problème de permissions Docker

**Solution** :
```bash
# Linux : Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Ou utiliser sudo (non recommandé)
sudo docker-compose up -d
```

### 8. Performance

#### ❌ L'application est lente

**Causes possibles** : Trop de données, ressources limitées

**Solutions** :
```bash
# 1. Limiter la quantité de données
# Dans load_data.py, réduire la période ou le nombre d'entreprises

# 2. Augmenter les ressources Docker
# Docker Desktop > Settings > Resources

# 3. Indexer la base de données
docker-compose exec postgres psql -U cac40_user -d cac40_db
CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_date ON stock_prices(ticker, date);

# 4. Nettoyer les anciennes données
DELETE FROM stock_prices WHERE date < CURRENT_DATE - INTERVAL '1 year';
```

## Commandes de diagnostic

### Vérification complète du système

```bash
#!/bin/bash

echo "=== État des conteneurs ==="
docker-compose ps

echo -e "\n=== État de la base de données ==="
docker-compose exec postgres psql -U cac40_user -d cac40_db -c "SELECT COUNT(*) as companies FROM companies;"
docker-compose exec postgres psql -U cac40_user -d cac40_db -c "SELECT COUNT(*) as prices FROM stock_prices;"

echo -e "\n=== Test de l'API ==="
curl -s http://localhost:8000/health | python -m json.tool

echo -e "\n=== Espace disque Docker ==="
docker system df

echo -e "\n=== Logs récents ==="
docker-compose logs --tail=20
```

### Script de réinitialisation complète

```bash
#!/bin/bash

echo "⚠️  ATTENTION : Cela va supprimer toutes les données !"
read -p "Continuer ? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Nettoyage complet..."
    docker-compose down -v
    docker system prune -f
    
    echo "🔨 Reconstruction..."
    ./install.sh
    
    echo "✅ Réinitialisation terminée"
fi
```

## Obtenir de l'aide

Si les solutions ci-dessus ne fonctionnent pas :

1. **Vérifier les logs détaillés** :
   ```bash
   docker-compose logs --tail=100 > logs.txt
   ```

2. **Informations système** :
   ```bash
   docker version
   docker-compose version
   uname -a
   ```

3. **État complet** :
   ```bash
   docker-compose ps
   docker stats --no-stream
   ```

4. **Créer un rapport** avec toutes ces informations

## Prévention des problèmes

### Bonnes pratiques

1. **Sauvegarder régulièrement** :
   ```bash
   docker-compose exec postgres pg_dump -U cac40_user cac40_db > backup.sql
   ```

2. **Monitorer l'espace disque** :
   ```bash
   docker system df
   ```

3. **Mettre à jour régulièrement** :
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   ```

4. **Tester après chaque modification** :
   ```bash
   python test_api.py
   ```

5. **Garder des logs** :
   ```bash
   docker-compose logs > logs_$(date +%Y%m%d).txt
   ```
