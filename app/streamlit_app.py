import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="CAC 40 Dashboard",
    page_icon="📈",
    layout="wide"
)

# URL de l'API
API_URL = "http://localhost:8000"

# Titre principal
st.title("📈 Dashboard CAC 40")
st.markdown("---")


def call_api(endpoint):
    """Appelle l'API et retourne les données"""
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de l'appel API: {str(e)}")
        return None


# Sidebar pour la navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Vue d'ensemble", "Analyse d'entreprise", "Comparaison", "Top Performers"]
)


if page == "Vue d'ensemble":
    st.header("Vue d'ensemble du CAC 40")
    
    # Récupération des données de santé
    health = call_api("/health")
    if health:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Entreprises", health.get("companies", 0))
        with col2:
            st.metric("Enregistrements", health.get("price_records", 0))
        with col3:
            status = health.get("status", "unknown")
            st.metric("Statut", status)
    
    st.markdown("---")
    
    # Liste des entreprises par secteur
    st.subheader("Entreprises par secteur")
    companies = call_api("/companies")
    
    if companies:
        df = pd.DataFrame(companies)
        
        # Comptage par secteur
        sector_counts = df['sector'].value_counts()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(
                sector_counts.reset_index().rename(
                    columns={'index': 'Secteur', 'sector': 'Nombre'}
                ),
                hide_index=True
            )
        
        with col2:
            fig = go.Figure(data=[go.Pie(
                labels=sector_counts.index,
                values=sector_counts.values,
                hole=0.3
            )])
            fig.update_layout(title="Répartition par secteur")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Liste complète des entreprises")
        st.dataframe(
            df[['ticker', 'name', 'sector']].sort_values('name'),
            hide_index=True,
            use_container_width=True
        )


elif page == "Analyse d'entreprise":
    st.header("Analyse d'entreprise")
    
    # Sélection de l'entreprise
    companies = call_api("/companies")
    
    if companies:
        company_dict = {f"{c['name']} ({c['ticker']})": c['ticker'] for c in companies}
        selected = st.selectbox("Sélectionnez une entreprise", list(company_dict.keys()))
        ticker = company_dict[selected]
        
        # Période d'analyse
        col1, col2 = st.columns(2)
        with col1:
            days = st.slider("Période (jours)", 7, 365, 90)
        
        # Récupération des données
        prices = call_api(f"/prices/{ticker}?limit={days}")
        stats = call_api(f"/statistics/{ticker}?days={days}")
        
        if stats:
            st.subheader(f"Statistiques - {stats['name']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Prix moyen", f"{stats['avg_close']:.2f} €")
            with col2:
                st.metric("Prix minimum", f"{stats['min_close']:.2f} €")
            with col3:
                st.metric("Prix maximum", f"{stats['max_close']:.2f} €")
            with col4:
                st.metric("Volume total", f"{stats['total_volume']:,.0f}")
        
        if prices:
            df = pd.DataFrame(prices)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Graphique des prix
            st.subheader("Évolution du cours")
            
            fig = go.Figure()
            
            # Chandelier
            fig.add_trace(go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Prix'
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Prix (€)",
                height=500,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Graphique du volume
            st.subheader("Volume de transactions")
            
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume'
            ))
            
            fig_volume.update_layout(
                xaxis_title="Date",
                yaxis_title="Volume",
                height=300
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
            
            # Tableau des données
            with st.expander("Voir les données brutes"):
                st.dataframe(
                    df[['date', 'open', 'high', 'low', 'close', 'volume']].sort_values('date', ascending=False),
                    hide_index=True,
                    use_container_width=True
                )


elif page == "Comparaison":
    st.header("Comparaison d'entreprises")
    
    companies = call_api("/companies")
    
    if companies:
        company_dict = {f"{c['name']} ({c['ticker']})": c['ticker'] for c in companies}
        
        selected_companies = st.multiselect(
            "Sélectionnez des entreprises à comparer (max 5)",
            list(company_dict.keys()),
            max_selections=5
        )
        
        if selected_companies:
            days = st.slider("Période (jours)", 7, 365, 90)
            
            fig = go.Figure()
            
            for company in selected_companies:
                ticker = company_dict[company]
                prices = call_api(f"/prices/{ticker}?limit={days}")
                
                if prices:
                    df = pd.DataFrame(prices)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # Normalisation à 100 pour comparaison
                    df['normalized'] = (df['close'] / df['close'].iloc[0]) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=df['date'],
                        y=df['normalized'],
                        mode='lines',
                        name=company.split('(')[0].strip()
                    ))
            
            fig.update_layout(
                title="Performance comparative (base 100)",
                xaxis_title="Date",
                yaxis_title="Performance (%)",
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)


elif page == "Top Performers":
    st.header("Meilleures performances")
    
    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("Période (jours)", 7, 365, 30)
    with col2:
        limit = st.slider("Nombre d'entreprises", 5, 40, 10)
    
    data = call_api(f"/top-performers?days={days}&limit={limit}")
    
    if data:
        performers = data.get("top_performers", [])
        
        if performers:
            df = pd.DataFrame(performers)
            
            # Graphique en barres
            fig = go.Figure()
            
            colors = ['green' if x > 0 else 'red' for x in df['performance']]
            
            fig.add_trace(go.Bar(
                x=df['performance'],
                y=df['name'],
                orientation='h',
                marker_color=colors,
                text=df['performance'].apply(lambda x: f"{x:.2f}%"),
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f"Top {limit} Performers ({days} jours)",
                xaxis_title="Performance (%)",
                yaxis_title="Entreprise",
                height=max(400, limit * 40),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.subheader("Détails")
            display_df = df[['name', 'ticker', 'sector', 'performance', 'start_price', 'end_price']]
            display_df.columns = ['Entreprise', 'Ticker', 'Secteur', 'Performance (%)', 'Prix début', 'Prix fin']
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Performance (%)": st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
                    "Prix début": st.column_config.NumberColumn(
                        format="%.2f €"
                    ),
                    "Prix fin": st.column_config.NumberColumn(
                        format="%.2f €"
                    )
                }
            )


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### À propos")
st.sidebar.info(
    "Dashboard CAC 40\n\n"
    "Données fournies par Yahoo Finance via yfinance\n\n"
    "API disponible à: http://localhost:8000/docs"
)
