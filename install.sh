#!/bin/bash

echo "🚀 Installation du projet CAC 40 Data Pipeline"
echo "================================================"

# Installation des dépendances Python sur l'hôte
echo "📦 Installation des dépendances Python sur Ubuntu..."
pip3 install --quiet --break-system-packages yfinance pandas psycopg2-binary 2>/dev/null || {
    python3 -m pip install --break-system-packages yfinance pandas psycopg2-binary
}

# Arrêt et nettoyage des conteneurs existants
echo "🧹 Nettoyage des conteneurs existants..."
docker-compose down -v

# Construction des images
echo "🔨 Construction des images Docker..."
docker-compose build

# Démarrage des services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attente que PostgreSQL soit prêt
echo "⏳ Attente de la disponibilité de PostgreSQL..."
sleep 10

# Chargement des données depuis l'hôte Ubuntu
echo "📊 Chargement des données du CAC 40 depuis l'hôte Ubuntu..."
python3 << 'PYTHON_SCRIPT'
import yfinance as yf
import psycopg2
from datetime import datetime, timedelta
import time

print("\n" + "="*60)
print("🚀 CHARGEMENT DES DONNÉES CAC 40")
print("="*60 + "\n")

# Connexion PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="cac40_db",
        user="cac40_user",
        password="cac40_password"
    )
    cur = conn.cursor()
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
    exit(1)

# Entreprises CAC 40
CAC40_COMPANIES = {
    "AIR.PA": {"name": "Airbus", "sector": "Industrials"},
    "AI.PA": {"name": "Air Liquide", "sector": "Materials"},
    "BNP.PA": {"name": "BNP Paribas", "sector": "Financials"},
    "MC.PA": {"name": "LVMH", "sector": "Consumer Discretionary"},
    "OR.PA": {"name": "L'Oréal", "sector": "Consumer Staples"},
    "SAN.PA": {"name": "Sanofi", "sector": "Healthcare"},
    "FP.PA": {"name": "TotalEnergies", "sector": "Energy"},
    "KER.PA": {"name": "Kering", "sector": "Consumer Discretionary"},
    "RMS.PA": {"name": "Hermès", "sector": "Consumer Discretionary"},
    "CA.PA": {"name": "Carrefour", "sector": "Consumer Staples"},
    "CAP.PA": {"name": "Capgemini", "sector": "Technology"},
    "ACA.PA": {"name": "Crédit Agricole", "sector": "Financials"},
    "BN.PA": {"name": "Danone", "sector": "Consumer Staples"},
    "ENGI.PA": {"name": "Engie", "sector": "Utilities"},
    "LR.PA": {"name": "Legrand", "sector": "Industrials"},
}

# Créer les tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR UNIQUE,
        name VARCHAR,
        sector VARCHAR
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR,
        date DATE,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume FLOAT,
        adj_close FLOAT,
        UNIQUE(ticker, date)
    )
""")
conn.commit()

# Charger les entreprises
print("📋 Chargement de la liste des entreprises...")
for ticker, info in CAC40_COMPANIES.items():
    cur.execute(
        "INSERT INTO companies (ticker, name, sector) VALUES (%s, %s, %s) ON CONFLICT (ticker) DO NOTHING",
        (ticker, info["name"], info["sector"])
    )
conn.commit()
print(f"✅ {len(CAC40_COMPANIES)} entreprises chargées\n")

# Télécharger les données
end_date = datetime.now()
start_date = end_date - timedelta(days=730)

print(f"📊 Téléchargement des données historiques...")
print(f"   Période: {start_date.date()} → {end_date.date()}\n")

total = 0
success = 0

for ticker in CAC40_COMPANIES.keys():
    print(f"   {ticker:12s} ", end="", flush=True)
    time.sleep(1)
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print("⚠️  Pas de données")
            continue
        
        count = 0
        for date, row in hist.iterrows():
            try:
                cur.execute(
                    """
                    INSERT INTO stock_prices (ticker, date, open, high, low, close, volume, adj_close)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker, date) DO NOTHING
                    """,
                    (ticker, date.date(), float(row['Open']), float(row['High']), 
                     float(row['Low']), float(row['Close']), float(row['Volume']), float(row['Close']))
                )
                count += 1
            except:
                pass
        
        conn.commit()
        total += count
        success += 1
        print(f"✅ {count:4d} enregistrements")
        
    except Exception as e:
        print(f"❌ {str(e)[:50]}")

print("\n" + "="*60)
print(f"✅ CHARGEMENT TERMINÉ")
print(f"   Succès: {success}/{len(CAC40_COMPANIES)} entreprises")
print(f"   Total: {total} enregistrements ajoutés")
print("="*60 + "\n")

cur.close()
conn.close()
PYTHON_SCRIPT

echo ""
echo "✅ Installation terminée !"
echo ""
echo "📋 Services disponibles :"
echo "   - PostgreSQL : localhost:5433"
echo "   - API FastAPI : http://localhost:8001"
echo "   - Documentation API : http://localhost:8001/docs"
echo "   - Streamlit : http://localhost:8502"
echo ""
echo "Pour lancer l'application : ./run.sh"
echo "Pour arrêter les services : docker-compose down"