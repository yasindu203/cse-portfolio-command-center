import requests
import sqlite3
import pandas as pd
import xml.etree.ElementTree as ET

def get_portfolio_watchlist(db_filepath="portfolio.db"):
    """Pulls current holdings and maps them to real company names for news searching."""
    try:
        conn = sqlite3.connect(db_filepath)
        df = pd.read_sql_query("SELECT ticker FROM current_holdings", conn)
        conn.close()
        
        if df.empty:
            return []
            
        # Map tickers to actual company names for better Google News results
        company_map = {
            'COMB': 'Commercial Bank', 'HNB': 'Hatton National Bank', 
            'SAMP': 'Sampath Bank', 'JKH': 'John Keells Holdings',
            'HAYL': 'Hayleys', 'KHL': 'Keells Hotels', 
            'OSEA': 'Overseas Realty', 'WLTH': 'Wealth Trust'
        }
        
        watchlist = []
        for ticker in df['ticker']:
            base_ticker = ticker.split('.')[0]
            name = company_map.get(base_ticker, base_ticker)
            watchlist.append({'ticker': base_ticker, 'name': name})
            
        return watchlist
    except Exception as e:
        print(f"Database error: {e}")
        return []

def scrape_corporate_news(watchlist):
    """Scrapes LIVE news using the Google News RSS feed."""
    alerts_generated = []
    
    # Keywords to trigger alerts
    alert_keywords = ['dividend', 'director', 'resignation', 'rights', 'earnings', 'profit', 'quarter']
    
    for company in watchlist:
        # Format the search query for Google News
        query = f"{company['name']} Sri Lanka"
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"
        
        try:
            response = requests.get(url, timeout=10)
            root = ET.fromstring(response.content)
            
            # Check the top 2 most recent articles for each company
            for item in root.findall('.//item')[:2]:
                headline = item.find('title').text
                # Clean up the RSS date string
                pub_date = item.find('pubDate').text[5:16] 
                
                headline_lower = headline.lower()
                
                for keyword in alert_keywords:
                    if keyword in headline_lower:
                        alerts_generated.append({
                            'Date': pub_date,
                            'Company': company['ticker'],
                            'Trigger': keyword.upper(),
                            'Headline': headline
                        })
                        break 
        except Exception:
            continue

    return alerts_generated