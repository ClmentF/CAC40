# 📁 Structure du projet CAC 40 Data Pipeline

## Vue d'ensemble

```
cac40-data-pipeline/
│
├── 📄 Configuration Docker
│   ├── docker-compose.yml      # Orchestration des services
│   ├── Dockerfile              # Image de l'application
│   └── .dockerignore           # Fichiers ignorés par Docker
│
├── 📄 Configuration Python
│   ├── requirements.txt        # Dépendances Python
│   └── .env.example           # Variables d'environnement (exemple)
│
├── 🔧 Scripts de gestion
│   ├── install.sh             # Installation et chargement initial
│   ├── run.sh                 # Lancement de l'application
│   ├── stop.sh                # Arrêt de l'application
│   ├── update_data.sh         # Mise à jour des données
│   ├── test_api.py            # Tests de l'API
│   └── Makefile               # Commandes simplifiées
│
├── 📱 Application
│   └── app/
│       ├── __init__.py        # Package Python
│       ├── database.py        # Configuration PostgreSQL + modèles SQLAlchemy
│       ├── load_data.py       # Script de chargement des données yfinance
│       ├── api.py             # API REST FastAPI
│       └── streamlit_app.py   # Interface utilisateur Streamlit
│
└── 📚 Documentation
    ├── README.md              # Documentation complète
    ├── QUICKSTART.md          # Guide de démarrage rapide
    ├── STRUCTURE.md           # Ce fichier
    └── .gitignore            # Fichiers ignorés par Git
```

## Description des fichiers

### 🐳 Configuration Docker

**docker-compose.yml**
- Définit 2 services : postgres (base de données) et app (application)
- Configure les ports, volumes et variables d'environnement
- Healthcheck pour PostgreSQL

**Dockerfile**
- Basé sur Python 3.11-slim
- Installe les dépendances système et Python
- Configure le répertoire de travail /app

### 🐍 Configuration Python

**requirements.txt**
- yfinance : récupération des données financières
- sqlalchemy & psycopg2 : interaction avec PostgreSQL
- fastapi & uvicorn : serveur API REST
- streamlit : interface web
- pandas : manipulation des données

### 🔨 Scripts de gestion

**install.sh**
- Nettoie les conteneurs existants
- Build les images Docker
- Démarre les services
- Lance le chargement initial des données

**run.sh**
- Vérifie que les conteneurs sont démarrés
- Lance l'API FastAPI en arrière-plan
- Lance l'interface Streamlit

**stop.sh**
- Arrête proprement tous les services

**update_data.sh**
- Met à jour les données sans tout réinstaller
- Utile pour récupérer les derniers prix

**test_api.py**
- Script de test pour vérifier tous les endpoints
- Affiche les résultats avec codes couleur

### 📱 Code de l'application

**app/database.py**
- Configuration de la connexion PostgreSQL
- Modèles SQLAlchemy :
  - `Company` : entreprises du CAC 40
  - `StockPrice` : données de prix historiques
- Fonctions d'initialisation et de session

**app/load_data.py**
- Liste des 34 entreprises du CAC 40
- Fonction pour charger la liste des entreprises
- Fonction pour télécharger les données yfinance
- Charge 2 ans de données historiques

**app/api.py**
- API REST avec FastAPI
- 8 endpoints principaux :
  - `/` : informations sur l'API
  - `/companies` : liste des entreprises
  - `/sectors` : liste des secteurs
  - `/prices/{ticker}` : historique des prix
  - `/latest/{ticker}` : dernier prix
  - `/statistics/{ticker}` : statistiques
  - `/top-performers` : meilleures performances
  - `/health` : état de santé

**app/streamlit_app.py**
- Interface web interactive
- 4 pages :
  1. Vue d'ensemble : stats globales
  2. Analyse d'entreprise : graphiques détaillés
  3. Comparaison : compare plusieurs entreprises
  4. Top Performers : classement des performances

## Flux de données

```
Yahoo Finance (yfinance)
         ↓
    load_data.py
         ↓
    PostgreSQL
         ↓
      API (FastAPI)
         ↓
    Streamlit Dashboard
```

## Ports utilisés

- **5432** : PostgreSQL
- **8000** : API FastAPI
- **8501** : Streamlit

## Base de données

### Table `companies`
- `id` : identifiant unique
- `ticker` : symbole Yahoo Finance (ex: MC.PA)
- `name` : nom de l'entreprise
- `sector` : secteur d'activité

### Table `stock_prices`
- `id` : identifiant unique
- `ticker` : référence à l'entreprise
- `date` : date de la cotation
- `open`, `high`, `low`, `close` : prix
- `volume` : volume de transactions
- `adj_close` : prix ajusté

## Volumes Docker

**postgres_data**
- Persiste les données PostgreSQL
- Conservé entre les redémarrages
- Supprimé avec `docker-compose down -v`

**./app → /app**
- Monte le code source dans le conteneur
- Permet le développement en temps réel
- Les modifications sont immédiatement disponibles

## Variables d'environnement

Définies dans `docker-compose.yml` :
- `DB_HOST`, `DB_PORT`, `DB_NAME`
- `DB_USER`, `DB_PASSWORD`

## Workflow de développement

1. Modifier le code dans `app/`
2. Les changements sont automatiques pour Streamlit
3. Pour l'API : rechargement auto avec `--reload`
4. Pour les modèles DB : redémarrer le conteneur

## Commandes Docker utiles

```bash
# Logs d'un service
docker-compose logs postgres
docker-compose logs app

# Shell dans un conteneur
docker-compose exec app bash
docker-compose exec postgres bash

# Connexion PostgreSQL
docker-compose exec postgres psql -U cac40_user -d cac40_db

# Redémarrer un service
docker-compose restart app
```
