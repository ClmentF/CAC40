# 💡 Exemples d'utilisation avancés

## 1. Utilisation de l'API avec Python

### Installation des dépendances
```bash
pip install requests pandas matplotlib
```

### Exemple 1 : Analyse d'une entreprise

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Configuration
API_URL = "http://localhost:8000"
TICKER = "MC.PA"  # LVMH

# Récupérer les données
response = requests.get(f"{API_URL}/prices/{TICKER}?limit=90")
data = response.json()

# Convertir en DataFrame
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Tracer le graphique
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['close'], label='Prix de clôture')
plt.title(f'Évolution du cours de {TICKER}')
plt.xlabel('Date')
plt.ylabel('Prix (€)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Exemple 2 : Comparaison de plusieurs entreprises

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"
TICKERS = ["MC.PA", "OR.PA", "KER.PA"]  # LVMH, L'Oréal, Kering
NAMES = ["LVMH", "L'Oréal", "Kering"]

plt.figure(figsize=(14, 7))

for ticker, name in zip(TICKERS, NAMES):
    response = requests.get(f"{API_URL}/prices/{ticker}?limit=180")
    data = response.json()
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Normalisation à 100
    df['normalized'] = (df['close'] / df['close'].iloc[0]) * 100
    
    plt.plot(df['date'], df['normalized'], label=name, linewidth=2)

plt.title('Performance comparative (base 100)', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Performance (%)', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Exemple 3 : Top performers avec visualisation

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"

# Récupérer les top performers
response = requests.get(f"{API_URL}/top-performers?days=90&limit=10")
data = response.json()

df = pd.DataFrame(data['top_performers'])

# Créer un graphique en barres
fig, ax = plt.subplots(figsize=(12, 8))

colors = ['green' if x > 0 else 'red' for x in df['performance']]
bars = ax.barh(df['name'], df['performance'], color=colors, alpha=0.7)

ax.set_xlabel('Performance (%)', fontsize=12)
ax.set_title('Top 10 Performers - 90 derniers jours', fontsize=16)
ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax.grid(True, axis='x', alpha=0.3)

# Ajouter les valeurs
for bar in bars:
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2,
            f'{width:.2f}%',
            ha='left' if width > 0 else 'right',
            va='center',
            fontsize=10)

plt.tight_layout()
plt.show()
```

## 2. Analyse statistique avancée

### Calcul de volatilité

```python
import requests
import pandas as pd
import numpy as np

API_URL = "http://localhost:8000"
TICKER = "MC.PA"

response = requests.get(f"{API_URL}/prices/{TICKER}?limit=90")
data = response.json()

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Calcul des rendements quotidiens
df['returns'] = df['close'].pct_change()

# Volatilité (écart-type des rendements)
volatility = df['returns'].std() * np.sqrt(252)  # Annualisée
print(f"Volatilité annualisée de {TICKER}: {volatility:.2%}")

# Rendement moyen
avg_return = df['returns'].mean() * 252  # Annualisé
print(f"Rendement moyen annualisé: {avg_return:.2%}")
```

### Corrélation entre entreprises

```python
import requests
import pandas as pd

API_URL = "http://localhost:8000"
TICKERS = ["MC.PA", "OR.PA", "KER.PA", "AI.PA", "BNP.PA"]

# Récupérer les données pour toutes les entreprises
all_data = {}
for ticker in TICKERS:
    response = requests.get(f"{API_URL}/prices/{ticker}?limit=180")
    data = response.json()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').set_index('date')
    all_data[ticker] = df['close']

# Créer un DataFrame avec tous les prix
prices_df = pd.DataFrame(all_data)

# Calculer les rendements
returns_df = prices_df.pct_change().dropna()

# Matrice de corrélation
correlation = returns_df.corr()
print("\nMatrice de corrélation:")
print(correlation)

# Visualisation
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Corrélation des rendements', fontsize=16)
plt.tight_layout()
plt.show()
```

## 3. Export des données

### Export vers CSV

```python
import requests
import pandas as pd

API_URL = "http://localhost:8000"

# Récupérer toutes les entreprises
response = requests.get(f"{API_URL}/companies")
companies = response.json()

# Pour chaque entreprise, récupérer les données
for company in companies[:5]:  # Limité à 5 pour l'exemple
    ticker = company['ticker']
    name = company['name']
    
    response = requests.get(f"{API_URL}/prices/{ticker}?limit=365")
    data = response.json()
    
    df = pd.DataFrame(data)
    df = df.sort_values('date')
    
    # Sauvegarder en CSV
    filename = f"{ticker.replace('.', '_')}_data.csv"
    df.to_csv(filename, index=False)
    print(f"Données de {name} sauvegardées dans {filename}")
```

### Export vers Excel avec plusieurs feuilles

```python
import requests
import pandas as pd

API_URL = "http://localhost:8000"
TICKERS = ["MC.PA", "OR.PA", "BNP.PA"]

with pd.ExcelWriter('cac40_analysis.xlsx') as writer:
    for ticker in TICKERS:
        response = requests.get(f"{API_URL}/prices/{ticker}?limit=180")
        data = response.json()
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        
        # Une feuille par entreprise
        sheet_name = ticker.replace('.PA', '')
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Fichier Excel créé: cac40_analysis.xlsx")
```

## 4. Requêtes SQL directes

### Via psql

```bash
docker-compose exec postgres psql -U cac40_user -d cac40_db

-- Voir toutes les entreprises
SELECT * FROM companies ORDER BY name;

-- Prix moyens par entreprise sur 30 jours
SELECT 
    c.name,
    c.ticker,
    AVG(sp.close) as avg_price,
    MIN(sp.close) as min_price,
    MAX(sp.close) as max_price
FROM companies c
JOIN stock_prices sp ON c.ticker = sp.ticker
WHERE sp.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.name, c.ticker
ORDER BY avg_price DESC;

-- Volume total par secteur
SELECT 
    c.sector,
    SUM(sp.volume) as total_volume,
    COUNT(DISTINCT c.ticker) as nb_companies
FROM companies c
JOIN stock_prices sp ON c.ticker = sp.ticker
GROUP BY c.sector
ORDER BY total_volume DESC;

-- Évolution mensuelle moyenne
SELECT 
    DATE_TRUNC('month', sp.date) as month,
    AVG(sp.close) as avg_price
FROM stock_prices sp
WHERE sp.ticker = 'MC.PA'
GROUP BY month
ORDER BY month DESC;
```

### Via Python avec SQLAlchemy

```python
from sqlalchemy import create_engine, text
import pandas as pd

# Connexion
engine = create_engine(
    "postgresql://cac40_user:cac40_password@localhost:5432/cac40_db"
)

# Requête personnalisée
query = """
SELECT 
    c.name,
    c.sector,
    sp.date,
    sp.close
FROM companies c
JOIN stock_prices sp ON c.ticker = sp.ticker
WHERE sp.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY sp.date DESC, c.name
"""

df = pd.read_sql(query, engine)
print(df)
```

## 5. Alertes et notifications

### Script d'alerte sur variation de prix

```python
import requests
import smtplib
from email.mime.text import MIMEText

API_URL = "http://localhost:8000"
ALERT_THRESHOLD = 5  # Alerte si variation > 5%

def check_alerts():
    response = requests.get(f"{API_URL}/top-performers?days=1&limit=40")
    data = response.json()
    
    alerts = []
    for company in data['top_performers']:
        if abs(company['performance']) > ALERT_THRESHOLD:
            alerts.append(company)
    
    if alerts:
        message = "🚨 Alertes de variation importante:\n\n"
        for alert in alerts:
            message += f"- {alert['name']}: {alert['performance']:.2f}%\n"
        
        print(message)
        # Ici vous pourriez envoyer un email ou une notification

if __name__ == "__main__":
    check_alerts()
```

## 6. Automatisation avec cron

### Mise à jour automatique quotidienne

Ajoutez dans votre crontab:

```bash
# Mise à jour tous les jours à 19h (après fermeture de la bourse)
0 19 * * 1-5 cd /chemin/vers/projet && ./update_data.sh
```

## 7. Analyse par secteur

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"

# Récupérer les entreprises par secteur
response = requests.get(f"{API_URL}/companies")
companies = response.json()

df_companies = pd.DataFrame(companies)

# Calculer la performance moyenne par secteur
sector_performance = {}

for sector in df_companies['sector'].unique():
    sector_companies = df_companies[df_companies['sector'] == sector]
    
    performances = []
    for ticker in sector_companies['ticker']:
        try:
            response = requests.get(
                f"{API_URL}/statistics/{ticker}?days=90"
            )
            stats = response.json()
            
            # Calculer une performance simple
            response = requests.get(f"{API_URL}/prices/{ticker}?limit=90")
            prices = response.json()
            if len(prices) > 1:
                first_price = prices[-1]['close']
                last_price = prices[0]['close']
                perf = ((last_price - first_price) / first_price) * 100
                performances.append(perf)
        except:
            pass
    
    if performances:
        sector_performance[sector] = sum(performances) / len(performances)

# Visualisation
sectors = list(sector_performance.keys())
perfs = list(sector_performance.values())

plt.figure(figsize=(12, 6))
colors = ['green' if x > 0 else 'red' for x in perfs]
plt.barh(sectors, perfs, color=colors, alpha=0.7)
plt.xlabel('Performance moyenne (%)')
plt.title('Performance par secteur - 90 derniers jours')
plt.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
plt.grid(True, axis='x', alpha=0.3)
plt.tight_layout()
plt.show()
```

## 8. Dashboard personnalisé avec Plotly Dash

```python
from dash import Dash, html, dcc, callback, Input, Output
import plotly.graph_objects as go
import requests
import pandas as pd

API_URL = "http://localhost:8000"

app = Dash(__name__)

# Récupérer la liste des entreprises
response = requests.get(f"{API_URL}/companies")
companies = response.json()
company_options = [
    {'label': f"{c['name']} ({c['ticker']})", 'value': c['ticker']}
    for c in companies
]

app.layout = html.Div([
    html.H1("CAC 40 Dashboard Custom"),
    dcc.Dropdown(
        id='ticker-dropdown',
        options=company_options,
        value='MC.PA'
    ),
    dcc.Graph(id='price-graph')
])

@callback(
    Output('price-graph', 'figure'),
    Input('ticker-dropdown', 'value')
)
def update_graph(ticker):
    response = requests.get(f"{API_URL}/prices/{ticker}?limit=180")
    data = response.json()
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    ))
    
    fig.update_layout(
        title=f'Évolution de {ticker}',
        yaxis_title='Prix (€)'
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
```

Ces exemples montrent la flexibilité et la puissance de votre pipeline de données CAC 40 !
