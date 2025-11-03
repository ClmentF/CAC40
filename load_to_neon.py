#!/usr/bin/env python3
"""
Script pour charger les données CAC40 dans Neon
Lancer : python3 load_to_neon.py
"""
import yfinance as yf
import psycopg2
from datetime import datetime, timedelta
import time

# ⚠️ REMPLACEZ cette ligne par votre connection string Neon
# Vous la trouvez sur Neon → Connect → Pooled connection
NEON_DATABASE_URL = 'postgresql://neondb_owner:npg_e1rSnZA8FQBj@ep-frosty-hat-abt8zw5w-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

print("="*60)
print("🚀 CHARGEMENT DES DONNÉES CAC40 VERS NEON")
print("="*60)

# Test de connexion
print("\n🔌 Connexion à Neon...", end=" ", flush=True)
try:
    conn = psycopg2.connect(NEON_DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connecté !\n")
except Exception as e:
    print(f"❌ Erreur de connexion")
    print(f"Détails : {e}")
    print("\n💡 Vérifiez :")
    print("  - Votre connection string est correcte")
    print("  - Votre IP est autorisée sur Neon (par défaut, tout est autorisé)")
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
print("📋 Création des tables...")
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

# Créer des index pour les performances
cur.execute("CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker ON stock_prices(ticker)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date)")

conn.commit()
print("✅ Tables et index créés\n")

# Charger les entreprises
print("📋 Chargement des entreprises...")
for ticker, info in CAC40_COMPANIES.items():
    cur.execute(
        "INSERT INTO companies (ticker, name, sector) VALUES (%s, %s, %s) ON CONFLICT (ticker) DO NOTHING",
        (ticker, info["name"], info["sector"])
    )
conn.commit()
print(f"✅ {len(CAC40_COMPANIES)} entreprises chargées\n")

# Télécharger les données
end_date = datetime.now()
start_date = end_date - timedelta(days=730)  # 2 ans de données

print(f"📊 Téléchargement des données historiques")
print(f"   Période: {start_date.date()} → {end_date.date()}")
print(f"   Entreprises: {len(CAC40_COMPANIES)}\n")

total = 0
success = 0
failed = 0

for idx, (ticker, info) in enumerate(CAC40_COMPANIES.items(), 1):
    print(f"   [{idx:2d}/{len(CAC40_COMPANIES)}] {info['name']:25s} ({ticker:10s}) ", end="", flush=True)
    time.sleep(1)  # Pause pour éviter rate limiting Yahoo
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print("⚠️  Pas de données")
            failed += 1
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
            except Exception as e:
                pass
        
        conn.commit()
        total += count
        success += 1
        print(f"✅ {count:4d} jours")
        
    except Exception as e:
        print(f"❌ Erreur")
        failed += 1

# Statistiques finales
print("\n" + "="*60)
print("✅ CHARGEMENT TERMINÉ")
print("="*60)
print(f"Entreprises avec succès : {success}/{len(CAC40_COMPANIES)}")
print(f"Entreprises échouées    : {failed}/{len(CAC40_COMPANIES)}")
print(f"Total enregistrements   : {total:,}")
print("="*60)

# Vérification
cur.execute("SELECT COUNT(*) FROM companies")
company_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM stock_prices")
price_count = cur.fetchone()[0]

print(f"\n📊 Vérification dans la base Neon :")
print(f"   Entreprises : {company_count}")
print(f"   Prix        : {price_count:,}")

cur.close()
conn.close()

print("\n✨ Vous pouvez maintenant visualiser vos données sur Neon.tech")
print("   Dashboard → SQL Editor → SELECT * FROM companies;")