from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from database import get_db, Company, StockPrice

app = FastAPI(
    title="CAC 40 Data API",
    description="API pour accéder aux données financières du CAC 40",
    version="1.0.0"
)


# Modèles Pydantic pour les réponses
class CompanyResponse(BaseModel):
    ticker: str
    name: str
    sector: str
    
    class Config:
        from_attributes = True


class StockPriceResponse(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    class Config:
        from_attributes = True


class StockStatistics(BaseModel):
    ticker: str
    name: str
    avg_close: float
    min_close: float
    max_close: float
    total_volume: float
    record_count: int


@app.get("/")
def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Bienvenue sur l'API CAC 40 Data",
        "version": "1.0.0",
        "endpoints": {
            "companies": "/companies",
            "prices": "/prices/{ticker}",
            "latest": "/latest/{ticker}",
            "statistics": "/statistics/{ticker}",
            "sectors": "/sectors",
            "top_performers": "/top-performers"
        }
    }


@app.get("/companies", response_model=List[CompanyResponse])
def get_companies(
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des entreprises du CAC 40"""
    query = db.query(Company)
    
    if sector:
        query = query.filter(Company.sector == sector)
    
    companies = query.all()
    return companies


@app.get("/sectors")
def get_sectors(db: Session = Depends(get_db)):
    """Récupère la liste des secteurs"""
    sectors = db.query(Company.sector).distinct().all()
    return {"sectors": [s[0] for s in sectors]}


@app.get("/prices/{ticker}", response_model=List[StockPriceResponse])
def get_prices(
    ticker: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Récupère les prix historiques pour un ticker"""
    # Vérifier que l'entreprise existe
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Ticker non trouvé")
    
    query = db.query(StockPrice).filter(StockPrice.ticker == ticker)
    
    if start_date:
        query = query.filter(StockPrice.date >= start_date)
    if end_date:
        query = query.filter(StockPrice.date <= end_date)
    
    prices = query.order_by(desc(StockPrice.date)).limit(limit).all()
    return prices


@app.get("/latest/{ticker}", response_model=StockPriceResponse)
def get_latest_price(ticker: str, db: Session = Depends(get_db)):
    """Récupère le dernier prix disponible pour un ticker"""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Ticker non trouvé")
    
    latest = db.query(StockPrice)\
        .filter(StockPrice.ticker == ticker)\
        .order_by(desc(StockPrice.date))\
        .first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible")
    
    return latest


@app.get("/statistics/{ticker}", response_model=StockStatistics)
def get_statistics(
    ticker: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Récupère des statistiques pour un ticker sur une période donnée"""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Ticker non trouvé")
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    stats = db.query(
        func.avg(StockPrice.close).label('avg_close'),
        func.min(StockPrice.close).label('min_close'),
        func.max(StockPrice.close).label('max_close'),
        func.sum(StockPrice.volume).label('total_volume'),
        func.count(StockPrice.id).label('record_count')
    ).filter(
        StockPrice.ticker == ticker,
        StockPrice.date >= cutoff_date
    ).first()
    
    return {
        "ticker": ticker,
        "name": company.name,
        "avg_close": float(stats.avg_close) if stats.avg_close else 0,
        "min_close": float(stats.min_close) if stats.min_close else 0,
        "max_close": float(stats.max_close) if stats.max_close else 0,
        "total_volume": float(stats.total_volume) if stats.total_volume else 0,
        "record_count": int(stats.record_count) if stats.record_count else 0
    }


@app.get("/top-performers")
def get_top_performers(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=40),
    db: Session = Depends(get_db)
):
    """Récupère les meilleures performances sur une période"""
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    # Récupérer toutes les entreprises
    companies = db.query(Company).all()
    performances = []
    
    for company in companies:
        # Prix au début de la période
        start_price = db.query(StockPrice.close)\
            .filter(StockPrice.ticker == company.ticker)\
            .filter(StockPrice.date >= cutoff_date)\
            .order_by(StockPrice.date)\
            .first()
        
        # Prix le plus récent
        end_price = db.query(StockPrice.close)\
            .filter(StockPrice.ticker == company.ticker)\
            .order_by(desc(StockPrice.date))\
            .first()
        
        if start_price and end_price:
            start_val = float(start_price[0])
            end_val = float(end_price[0])
            performance = ((end_val - start_val) / start_val) * 100
            
            performances.append({
                "ticker": company.ticker,
                "name": company.name,
                "sector": company.sector,
                "performance": round(performance, 2),
                "start_price": round(start_val, 2),
                "end_price": round(end_val, 2)
            })
    
    # Trier par performance
    performances.sort(key=lambda x: x['performance'], reverse=True)
    
    return {
        "period_days": days,
        "top_performers": performances[:limit]
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Vérifie la santé de l'API et de la base de données"""
    try:
        # Test de connexion à la DB
        company_count = db.query(Company).count()
        price_count = db.query(StockPrice).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "companies": company_count,
            "price_records": price_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de santé: {str(e)}")
