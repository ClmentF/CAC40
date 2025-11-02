# 📈 CAC 40 Data Pipeline

Projet complet pour récupérer, stocker et analyser les données financières des entreprises du CAC 40.

## 🏗️ Architecture

- **Docker** : Conteneurisation de l'application
- **PostgreSQL** : Base de données pour stocker les données financières
- **yfinance** : Récupération des données depuis Yahoo Finance
- **FastAPI** : API REST pour accéder aux données
- **Streamlit** : Interface web interactive

## 📁 Structure du projet

```
.
├── docker-compose.yml      # Orchestration des services
├── Dockerfile              # Image de l'application
├── requirements.txt        # Dépendances Python
├── install.sh             # Script d'installation
├── run.sh                 # Script de lancement
└── app/
    ├── database.py        # Configuration de la base de données
    ├── load_data.py       # Chargement des données yfinance
    ├── api.py             # API FastAPI
    └── streamlit_app.py   # Interface Streamlit
```

## 🚀 Installation

### Prérequis

- Docker et Docker Compose installés
- Git (optionnel)

### Étapes

1. **Téléchargez le projet**

2. **Rendez les scripts exécutables**
```bash
chmod +x install.sh run.sh
```

3. **Lancez l'installation**
```bash
./install.sh
```

Ce script va :
- Construire les images Docker
- Démarrer PostgreSQL
- Créer les tables
- Charger 2 ans de données pour ~34 entreprises du CAC 40

⏱️ L'installation prend environ 5-10 minutes.

## 🎯 Utilisation

### Lancer l'application

```bash
./run.sh
```

### Services disponibles

- **API FastAPI** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Streamlit Dashboard** : http://localhost:8501
- **PostgreSQL** : localhost:5432

### Identifiants PostgreSQL

- Database : `cac40_db`
- User : `cac40_user`
- Password : `cac40_password`

## 📊 Fonctionnalités

### API REST (FastAPI)

Endpoints disponibles :

- `GET /companies` - Liste des entreprises
- `GET /sectors` - Liste des secteurs
- `GET /prices/{ticker}` - Prix historiques
- `GET /latest/{ticker}` - Dernier prix
- `GET /statistics/{ticker}` - Statistiques
- `GET /top-performers` - Meilleures performances
- `GET /health` - État de l'API

**Exemples d'utilisation :**

```bash
# Liste des entreprises
curl http://localhost:8000/companies

# Prix de Total Energies sur 30 jours
curl "http://localhost:8000/prices/FP.PA?limit=30"

# Statistiques de LVMH sur 90 jours
curl "http://localhost:8000/statistics/MC.PA?days=90"

# Top 10 performers sur 30 jours
curl "http://localhost:8000/top-performers?days=30&limit=10"
```

### Dashboard Streamlit

Interface interactive avec :

1. **Vue d'ensemble** : Statistiques globales et répartition par secteur
2. **Analyse d'entreprise** : Graphiques de prix et volume pour une entreprise
3. **Comparaison** : Comparaison de performances entre plusieurs entreprises
4. **Top Performers** : Classement des meilleures performances

## 🔄 Mise à jour des données

Pour recharger les données (par exemple pour obtenir les derniers prix) :

```bash
docker-compose exec app python /app/load_data.py
```

## 🛑 Arrêt des services

```bash
docker-compose down
```

Pour supprimer également les données :

```bash
docker-compose down -v
```

## 📝 Exemples de requêtes Python

```python
import requests

# Récupérer la liste des entreprises
response = requests.get("http://localhost:8000/companies")
companies = response.json()

# Obtenir les prix de Airbus
response = requests.get("http://localhost:8000/prices/AIR.PA?limit=100")
prices = response.json()

# Statistiques de BNP Paribas sur 30 jours
response = requests.get("http://localhost:8000/statistics/BNP.PA?days=30")
stats = response.json()
```

## 🗃️ Accès direct à PostgreSQL

```bash
# Se connecter à la base de données
docker-compose exec postgres psql -U cac40_user -d cac40_db

# Exemples de requêtes SQL
SELECT * FROM companies;
SELECT * FROM stock_prices WHERE ticker = 'MC.PA' ORDER BY date DESC LIMIT 10;
SELECT ticker, COUNT(*) FROM stock_prices GROUP BY ticker;
```

## 🔧 Développement

Pour modifier l'application :

1. Éditez les fichiers dans le dossier `app/`
2. Les modifications sont automatiquement reflétées (volumes Docker)
3. Pour l'API : le mode `--reload` d'Uvicorn recharge automatiquement
4. Pour Streamlit : actualisez la page

## 🐛 Dépannage

**Les conteneurs ne démarrent pas :**
```bash
docker-compose logs
```

**Réinitialiser complètement :**
```bash
docker-compose down -v
./install.sh
```

**Port déjà utilisé :**
Modifiez les ports dans `docker-compose.yml`

## 📚 Entreprises incluses

Le projet couvre environ 34 entreprises majeures du CAC 40 :
- Airbus, Air Liquide, ArcelorMittal, AXA
- BNP Paribas, Bouygues, Capgemini, Carrefour
- Crédit Agricole, Danone, Engie, EssilorLuxottica
- Hermès, Kering, L'Oréal, LVMH
- Michelin, Orange, Pernod Ricard, Publicis
- Renault, Safran, Saint-Gobain, Sanofi
- Schneider Electric, Société Générale, Stellantis
- STMicroelectronics, TotalEnergies, Veolia, Vinci
- Et plus...

## 📄 Licence

Projet à usage éducatif et personnel.

Les données proviennent de Yahoo Finance via la bibliothèque yfinance.
