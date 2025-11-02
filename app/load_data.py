import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, SessionLocal, Company, StockPrice

# Liste des principales entreprises du CAC 40 avec leurs tickers Yahoo Finance
CAC40_COMPANIES = {
    "AIR.PA": {"name": "Airbus", "sector": "Industrials"},
    "AI.PA": {"name": "Air Liquide", "sector": "Materials"},
    "MT.AS": {"name": "ArcelorMittal", "sector": "Materials"},
    "CS.PA": {"name": "AXA", "sector": "Financials"},
    "BNP.PA": {"name": "BNP Paribas", "sector": "Financials"},
    "EN.PA": {"name": "Bouygues", "sector": "Industrials"},
    "CAP.PA": {"name": "Capgemini", "sector": "Technology"},
    "CA.PA": {"name": "Carrefour", "sector": "Consumer Staples"},
    "ACA.PA": {"name": "Crédit Agricole", "sector": "Financials"},
    "BN.PA": {"name": "Danone", "sector": "Consumer Staples"},
    "ENGI.PA": {"name": "Engie", "sector": "Utilities"},
    "EL.PA": {"name": "EssilorLuxottica", "sector": "Healthcare"},
    "RMS.PA": {"name": "Hermès", "sector": "Consumer Discretionary"},
    "KER.PA": {"name": "Kering", "sector": "Consumer Discretionary"},
    "OR.PA": {"name": "L'Oréal", "sector": "Consumer Staples"},
    "LR.PA": {"name": "Legrand", "sector": "Industrials"},
    "MC.PA": {"name": "LVMH", "sector": "Consumer Discretionary"},
    "ML.PA": {"name": "Michelin", "sector": "Consumer Discretionary"},
    "ORA.PA": {"name": "Orange", "sector": "Telecom"},
    "RI.PA": {"name": "Pernod Ricard", "sector": "Consumer Staples"},
    "PUB.PA": {"name": "Publicis", "sector": "Consumer Discretionary"},
    "RNO.PA": {"name": "Renault", "sector": "Consumer Discretionary"},
    "SAF.PA": {"name": "Safran", "sector": "Industrials"},
    "SGO.PA": {"name": "Saint-Gobain", "sector": "Industrials"},
    "SAN.PA": {"name": "Sanofi", "sector": "Healthcare"},
    "SU.PA": {"name": "Schneider Electric", "sector": "Industrials"},
    "GLE.PA": {"name": "Société Générale", "sector": "Financials"},
    "STLAM.PA": {"name": "Stellantis", "sector": "Consumer Discretionary"},
    "STMPA.PA": {"name": "STMicroelectronics", "sector": "Technology"},
    "FP.PA": {"name": "TotalEnergies", "sector": "Energy"},
    "URW.AS": {"name": "Unibail-Rodamco-Westfield", "sector": "Real Estate"},
    "VIE.PA": {"name": "Veolia", "sector": "Utilities"},
    "DG.PA": {"name": "Vinci", "sector": "Industrials"},
    "VIV.PA": {"name": "Vivendi", "sector": "Telecom"},
}


def load_companies(db):
    """Charge la liste des entreprises dans la base de données"""
    print("📋 Chargement de la liste des entreprises...")
    
    for ticker, info in CAC40_COMPANIES.items():
        company = db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            company = Company(
                ticker=ticker,
                name=info["name"],
                sector=info["sector"]
            )
            db.add(company)
    
    db.commit()
    print(f"✅ {len(CAC40_COMPANIES)} entreprises chargées")


def load_stock_data(db, ticker, start_date, end_date):
    """Charge les données historiques d'une action"""
    try:
        print(f"   Téléchargement de {ticker}...")
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"   ⚠️  Pas de données pour {ticker}")
            return 0
        
        count = 0
        for date, row in hist.iterrows():
            # Vérifier si l'entrée existe déjà
            existing = db.query(StockPrice).filter(
                StockPrice.ticker == ticker,
                StockPrice.date == date.date()
            ).first()
            
            if not existing:
                price = StockPrice(
                    ticker=ticker,
                    date=date.date(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume']),
                    adj_close=float(row['Close'])
                )
                db.add(price)
                count += 1
        
        if count > 0:
            db.commit()
        
        print(f"   ✅ {count} nouveaux enregistrements pour {ticker}")
        return count
        
    except Exception as e:
        print(f"   ❌ Erreur pour {ticker}: {str(e)}")
        db.rollback()
        return 0


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🚀 CHARGEMENT DES DONNÉES CAC 40")
    print("="*60 + "\n")
    
    # Initialisation de la base de données
    print("🔧 Initialisation de la base de données...")
    init_db()
    
    # Création d'une session
    db = SessionLocal()
    
    try:
        # Chargement des entreprises
        load_companies(db)
        
        # Période de téléchargement (2 ans de données)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        
        print(f"\n📊 Téléchargement des données historiques...")
        print(f"   Période: {start_date.date()} → {end_date.date()}\n")
        
        # Chargement des données pour chaque entreprise
        total_records = 0
        for ticker in CAC40_COMPANIES.keys():
            records = load_stock_data(db, ticker, start_date, end_date)
            total_records += records
        
        print(f"\n" + "="*60)
        print(f"✅ CHARGEMENT TERMINÉ")
        print(f"   Total: {total_records} enregistrements ajoutés")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
