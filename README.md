\# 📈 CSE Portfolio Command Center



A fully automated, local-first portfolio management terminal built specifically for retail investors in the Colombo Stock Exchange (CSE). 



This tool bypasses the lack of public APIs by utilizing a hybrid data ingestion model: automated live market data retrieval combined with a localized, script-based brokerage report ingestor. It functions as a complete, self-hosted financial terminal offering live valuations, quantitative trend analysis, and automated corporate intelligence scraping.



\## ✨ Core Features



\* \*\*Automated Ledger Management:\*\* Ingests raw CSV exports from Sri Lankan brokerages (like ATrad or DirectFN), cleans the data, and securely calculates your Weighted Average Cost of Capital (WACC) using a local SQLite database.

\* \*\*Live Market Sync:\*\* Bypasses blocked public APIs (like Yahoo Finance) to pull live, real-time market prices directly from the CSE's Trade Summary backend.

\* \*\*Quantitative Strategy Engine:\*\* Calculates the 200-Day Simple Moving Average (SMA) and 14-Day Relative Strength Index (RSI) to generate automated strategic trend flags (Uptrend/Downtrend, Overbought/Oversold).

\* \*\*Live Corporate Intelligence:\*\* A custom web scraper that monitors breaking market news and filters alerts (Dividends, Director Dealings, Earnings) specifically for the companies in your active portfolio.

\* \*\*Interactive UI:\*\* A modern, reactive dashboard built entirely in Python using Streamlit and Plotly.



\## 🛠️ Technology Stack



\* \*\*Backend \& Math:\*\* `Python`, `pandas`, `numpy`

\* \*\*Database:\*\* `SQLite3`

\* \*\*Frontend Visualization:\*\* `Streamlit`, `plotly`

\* \*\*Web Scraping \& APIs:\*\* `requests`, `BeautifulSoup4`, `xml.etree.ElementTree`



\## 🚀 Installation \& Setup



\*\*1. Clone the repository\*\*

```bash

git clone \[https://github.com/yourusername/cse-portfolio-command-center.git](https://github.com/yourusername/cse-portfolio-command-center.git)

cd cse-portfolio-command-center

