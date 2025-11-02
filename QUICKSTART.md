# 🚀 Guide de démarrage rapide

## Installation en 3 étapes

### 1. Préparation
```bash
chmod +x *.sh
```

### 2. Installation
```bash
./install.sh
```
⏱️ Durée : 5-10 minutes

### 3. Lancement
```bash
./run.sh
```

## 🌐 Accès aux services

- **Streamlit** : http://localhost:8501
- **API** : http://localhost:8000/docs
- **PostgreSQL** : localhost:5432

## 📝 Commandes utiles

```bash
# Mettre à jour les données
./update_data.sh

# Arrêter l'application
./stop.sh

# Tester l'API
python test_api.py

# Voir les logs
docker-compose logs -f

# Redémarrer complètement
docker-compose down -v
./install.sh
```

## 🎯 Exemples d'utilisation API

### Avec curl
```bash
# Liste des entreprises
curl http://localhost:8000/companies

# Prix de LVMH
curl http://localhost:8000/prices/MC.PA?limit=30

# Top performers
curl http://localhost:8000/top-performers?days=30
```

### Avec Python
```python
import requests

# Obtenir les entreprises
r = requests.get("http://localhost:8000/companies")
companies = r.json()

# Prix du jour
r = requests.get("http://localhost:8000/latest/MC.PA")
prix = r.json()
```

## 🔍 Accès à la base de données

```bash
# Se connecter
docker-compose exec postgres psql -U cac40_user -d cac40_db

# Requêtes SQL
SELECT * FROM companies;
SELECT * FROM stock_prices WHERE ticker = 'MC.PA' LIMIT 10;
```

## 🐛 Problèmes courants

**Port déjà utilisé ?**
→ Modifier les ports dans `docker-compose.yml`

**Conteneurs ne démarrent pas ?**
→ `docker-compose logs`

**Données manquantes ?**
→ `./update_data.sh`

**Réinitialisation complète ?**
→ `docker-compose down -v && ./install.sh`
