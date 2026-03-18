import pandas as pd
import sqlite3
import requests
import warnings

# Suppress warnings for a cleaner terminal output
warnings.filterwarnings('ignore')

def get_cse_live_prices():
    """Fetches live prices directly from the comprehensive CSE Trade Summary API."""
    import requests # ensure requests is imported
    print("Fetching live market data directly from the CSE API (Full Market)...")
    url = "https://www.cse.lk/api/tradeSummary"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=15)
        data = response.json()
        
        market_prices = {}
        trade_data = data.get('reqTradeSummery', [])
        
        for stock in trade_data:
            raw_symbol = stock.get('symbol', '')
            price = stock.get('price', 0.0)
            
            # THE FIX: Only accept ordinary voting shares to prevent overwrite
            if raw_symbol and raw_symbol.endswith('.N0000'):
                base_ticker = raw_symbol.split('.')[0]
                db_ticker = f"{base_ticker}.CM"
                
                if price > 0:
                    market_prices[db_ticker] = float(price)
            
        return market_prices
        
    except Exception as e:
        print(f"  [!] Failed to connect to CSE API: {e}")
        return {}
    

def run_analytics_engine(db_filepath="portfolio.db"):
    print("Initializing Portfolio Engine...")
    
    # 1. Connect to Database and read transactions
    conn = sqlite3.connect(db_filepath)
    df_tx = pd.read_sql_query("SELECT * FROM transactions", conn)
    
    if df_tx.empty:
        print("No transactions found in the database.")
        return

    # 2. Calculate Net Holdings & Average Cost
    print("Calculating Weighted Average Costs...")
    df_tx['signed_qty'] = df_tx.apply(lambda row: row['quantity'] if row['type'] == 'buy' else -row['quantity'], axis=1)
    
    holdings = df_tx.groupby('ticker')['signed_qty'].sum().reset_index()
    holdings.rename(columns={'signed_qty': 'total_quantity'}, inplace=True)
    holdings = holdings[holdings['total_quantity'] > 0]
    
    buys = df_tx[df_tx['type'] == 'buy'].groupby('ticker').apply(
        lambda x: (x['quantity'] * x['price']).sum() / x['quantity'].sum()
    ).reset_index(name='average_cost')
    
    portfolio = pd.merge(holdings, buys, on='ticker', how='left')

    # 3. Fetch Live Market Prices via CSE API
    live_prices_dict = get_cse_live_prices()
    
    # Map the fetched prices to our portfolio dataframe. If a stock isn't found, default to 0.0
    portfolio['live_price'] = portfolio['ticker'].map(live_prices_dict).fillna(0.0)

    # 4. Calculate Performance Metrics
    portfolio['total_cost'] = portfolio['total_quantity'] * portfolio['average_cost']
    portfolio['current_value'] = portfolio['total_quantity'] * portfolio['live_price']
    
    portfolio['unrealized_gain_lkr'] = portfolio['current_value'] - portfolio['total_cost']
    portfolio['roi_percent'] = (portfolio['unrealized_gain_lkr'] / portfolio['total_cost']) * 100

    # 5. Save the updated snapshot
    portfolio[['ticker', 'total_quantity', 'average_cost', 'live_price']].to_sql('current_holdings', conn, if_exists='replace', index=False)
    conn.close()

    # 6. Display the Results
    print("\n" + "="*70)
    print("LIVE PORTFOLIO SNAPSHOT".center(70))
    print("="*70)
    
    display_df = portfolio[['ticker', 'total_quantity', 'average_cost', 'live_price', 'unrealized_gain_lkr', 'roi_percent']].copy()
    display_df['roi_percent'] = display_df['roi_percent'].round(2).astype(str) + ' %'
    display_df['unrealized_gain_lkr'] = display_df['unrealized_gain_lkr'].round(2)
    display_df['average_cost'] = display_df['average_cost'].round(2)
    display_df['live_price'] = display_df['live_price'].round(2)
    
    print(display_df.to_string(index=False))
    print("="*70)
    
    total_portfolio_value = portfolio['current_value'].sum()
    total_profit = portfolio['unrealized_gain_lkr'].sum()
    print(f"TOTAL PORTFOLIO VALUE: LKR {total_portfolio_value:,.2f}")
    print(f"TOTAL UNREALIZED P/L:  LKR {total_profit:,.2f}")
    print("="*70 + "\n")

if __name__ == '__main__':
    run_analytics_engine()