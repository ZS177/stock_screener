# Quality Stock Screener

Screens ASX and US equities across four quality metrics:
- Gross margin > 40%
- Revenue growth > 8%
- Return on equity > 15%
- Debt/equity < 1.5x

Built with Python and yfinance. Outputs a ranked table 
and filtered list of stocks passing all criteria.

## Run it
pip install yfinance pandas
python stock_screener.py

## Customise it
Edit the TICKERS list and filter thresholds at the top of the file.
