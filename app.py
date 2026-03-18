import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from portfolio_engine import run_analytics_engine 
from quant_engine import analyze_technical_indicators
# Injecting the Intelligence Scraper
from intelligence_scraper import get_portfolio_watchlist, scrape_corporate_news 

st.set_page_config(page_title="CSE Portfolio Tracker", page_icon="📈", layout="wide")

st.title("📈 CSE Portfolio Command Center")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("System Controls")
st.sidebar.write("Use this panel to sync your local database with live CSE servers.")

if st.sidebar.button("🔄 Sync Live Market Data", width='stretch'):
    with st.spinner("Pinging CSE API for live prices..."):
        run_analytics_engine("portfolio.db")
    st.sidebar.success("Database Updated Successfully!")

# --- MAIN DASHBOARD ---
st.write("### Current Holdings Overview")

try:
    conn = sqlite3.connect("portfolio.db")
    df = pd.read_sql_query("SELECT * FROM current_holdings", conn)
    conn.close()
    
    if not df.empty:
        df['total_cost'] = df['total_quantity'] * df['average_cost']
        df['current_value'] = df['total_quantity'] * df['live_price']
        df['unrealized_gain_lkr'] = df['current_value'] - df['total_cost']
        df['roi'] = (df['unrealized_gain_lkr'] / df['total_cost']) * 100
        
        total_value = df['current_value'].sum()
        total_profit = df['unrealized_gain_lkr'].sum()
        total_cost_basis = total_value - total_profit
        total_roi = (total_profit / total_cost_basis) * 100 if total_cost_basis > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Portfolio Value", f"LKR {total_value:,.2f}")
        col2.metric("Total Unrealized Profit", f"LKR {total_profit:,.2f}", f"{total_roi:.2f}%")
        col3.metric("Total Active Holdings", f"{len(df)} Companies")
        
        st.divider()
        
        display_df = df[['ticker', 'total_quantity', 'average_cost', 'live_price', 'unrealized_gain_lkr', 'roi']].copy()
        display_df.columns = ['Ticker', 'Shares', 'Avg Cost (LKR)', 'Live Price (LKR)', 'P/L (LKR)', 'ROI (%)']
        
        st.dataframe(
            display_df.style.format({
                'Shares': '{:,.0f}',
                'Avg Cost (LKR)': '{:,.2f}',
                'Live Price (LKR)': '{:,.2f}',
                'P/L (LKR)': '{:,.2f}',
                'ROI (%)': '{:,.2f}%'
            }).map(lambda x: 'color: #00FF00' if x > 0 else 'color: #FF0000' if x < 0 else '', subset=['P/L (LKR)', 'ROI (%)']),
            width='stretch',
            hide_index=True
        )
        
        st.divider()
        
        # --- MODULE 2: PORTFOLIO ANALYTICS ---
        st.write("### Portfolio Analytics")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_pie = px.pie(
                df, values='current_value', names='ticker',
                title="Asset Allocation (by Value)", hole=0.4
            )
            fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie)
            
        with col_chart2:
            df['Color'] = df['unrealized_gain_lkr'].apply(lambda x: 'Profit' if x > 0 else 'Loss')
            fig_bar = px.bar(
                df, x='ticker', y='unrealized_gain_lkr',
                title="Unrealized Profit/Loss by Asset", color='Color',
                color_discrete_map={'Profit': '#2e7d32', 'Loss': '#d32f2f'},
                labels={'unrealized_gain_lkr': 'P/L (LKR)', 'ticker': 'Stock'}
            )
            fig_bar.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_bar)

        st.divider()

        # Create two columns for the bottom section to save vertical space
        col_quant, col_intel = st.columns([2, 1])

        # --- MODULE 3: QUANTITATIVE STRATEGY ---
        with col_quant:
            st.write("### Strategic Quantitative Analysis")
            st.caption("Powered by simulated 200-Day SMA and 14-Day RSI.")
            
            with st.spinner("Crunching technical indicators..."):
                quant_data = []
                unique_tickers = df['ticker'].unique()
                
                for ticker in unique_tickers:
                    report = analyze_technical_indicators(ticker)
                    if report:
                        quant_data.append(report)
                        
                if quant_data:
                    quant_df = pd.DataFrame(quant_data)
                    
                    def highlight_strategy(val):
                        if 'Uptrend' in str(val) or 'Buy' in str(val):
                            return 'color: #00FF00'
                        elif 'Downtrend' in str(val) or 'Pullback' in str(val):
                            return 'color: #FF0000'
                        else:
                            return 'color: #FFA500' 
                    
                    st.dataframe(
                        quant_df.style.map(highlight_strategy, subset=['Trend Status', 'RSI Signal']),
                        width='stretch',
                        hide_index=True
                    )

        # --- MODULE 4: CORPORATE INTELLIGENCE ALERTS ---
        with col_intel:
            st.write("### 🚨 Live Corporate Intelligence")
            st.caption("Monitoring market announcements for your holdings.")
            
            with st.spinner("Scanning for news..."):
                watchlist = get_portfolio_watchlist("portfolio.db")
                if watchlist:
                    alerts = scrape_corporate_news(watchlist)
                    
                    if alerts:
                        for alert in alerts:
                            # Use Streamlit's native error/warning banners for high visibility
                            if alert['Trigger'] == 'DIVIDEND':
                                st.success(f"**{alert['Company']} ({alert['Date']}):** {alert['Headline']}")
                            elif alert['Trigger'] == 'DIRECTOR DEALING':
                                st.warning(f"**{alert['Company']} ({alert['Date']}):** {alert['Headline']}")
                            else:
                                st.info(f"**{alert['Company']} ({alert['Date']}):** {alert['Headline']}")
                    else:
                        st.info("No new critical announcements for your holdings today.")
                else:
                    st.warning("Could not load watchlist.")
        
    else:
        st.info("No holdings found. Please drop your brokerage CSV and run the parser.")

except Exception as e:
    st.error(f"Error loading database: {e}")