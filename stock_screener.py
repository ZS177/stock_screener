import yfinance as yf
import pandas as pd

# ── UNIVERSE ─────────────────────────────────────────────────────────────────
# Mix of ASX and US quality growth stocks to screen
TICKERS = [
    # ASX
    "PME.AX", "WTC.AX", "ALU.AX", "XRO.AX", "REA.AX",
    "CAR.AX", "CPU.AX", "TLX.AX", "NEA.AX", "NXT.AX",
    # US
    "NVDA", "MSFT", "ADBE", "VEEV", "PAYC",
    "MNST", "ROP", "IDXX", "ODFL", "POOL"
]

# ── QUALITY FILTERS ───────────────────────────────────────────────────────────
MIN_GROSS_MARGIN = 0.40       # 40%+ gross margin
MIN_REVENUE_GROWTH = 0.08     # 8%+ revenue growth
MIN_RETURN_ON_EQUITY = 0.15   # 15%+ ROE
MAX_DEBT_TO_EQUITY = 1.5      # not overleveraged

# ── FETCH AND SCORE ───────────────────────────────────────────────────────────
def fetch_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        name = info.get("shortName", ticker)
        gross_margin = info.get("grossMargins", None)
        revenue_growth = info.get("revenueGrowth", None)
        roe = info.get("returnOnEquity", None)
        de_ratio = info.get("debtToEquity", None)
        pe_ratio = info.get("trailingPE", None)
        market_cap = info.get("marketCap", None)

        # convert D/E from percentage format if needed
        if de_ratio and de_ratio > 10:
            de_ratio = de_ratio / 100

        return {
            "Ticker": ticker,
            "Name": name[:28] if name else ticker,
            "Gross Margin": gross_margin,
            "Revenue Growth": revenue_growth,
            "ROE": roe,
            "D/E Ratio": de_ratio,
            "P/E Ratio": pe_ratio,
            "Market Cap ($B)": round(market_cap / 1e9, 1) if market_cap else None,
        }

    except Exception:
        return None


def score_stock(row):
    score = 0
    if row["Gross Margin"] and row["Gross Margin"] >= MIN_GROSS_MARGIN:
        score += 1
    if row["Revenue Growth"] and row["Revenue Growth"] >= MIN_REVENUE_GROWTH:
        score += 1
    if row["ROE"] and row["ROE"] >= MIN_RETURN_ON_EQUITY:
        score += 1
    if row["D/E Ratio"] is not None and row["D/E Ratio"] <= MAX_DEBT_TO_EQUITY:
        score += 1
    return score


def passes_filters(row):
    if row["Gross Margin"] is None or row["Revenue Growth"] is None:
        return False
    return (
        row["Gross Margin"] >= MIN_GROSS_MARGIN and
        row["Revenue Growth"] >= MIN_REVENUE_GROWTH and
        (row["ROE"] is None or row["ROE"] >= MIN_RETURN_ON_EQUITY) and
        (row["D/E Ratio"] is None or row["D/E Ratio"] <= MAX_DEBT_TO_EQUITY)
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────
print("\n── Fetching data... ──\n")

records = []
for ticker in TICKERS:
    print(f"  Pulling {ticker}...")
    data = fetch_metrics(ticker)
    if data:
        records.append(data)

df = pd.DataFrame(records)
df["Quality Score"] = df.apply(score_stock, axis=1)
df["Passes"] = df.apply(passes_filters, axis=1)

# format for display
display = df.copy()
display["Gross Margin"] = display["Gross Margin"].apply(lambda x: f"{x:.0%}" if x else "N/A")
display["Revenue Growth"] = display["Revenue Growth"].apply(lambda x: f"{x:.0%}" if x else "N/A")
display["ROE"] = display["ROE"].apply(lambda x: f"{x:.0%}" if x else "N/A")
display["D/E Ratio"] = display["D/E Ratio"].apply(lambda x: f"{x:.2f}" if x else "N/A")
display["P/E Ratio"] = display["P/E Ratio"].apply(lambda x: f"{x:.1f}x" if x else "N/A")
display["Market Cap ($B)"] = display["Market Cap ($B)"].apply(lambda x: f"${x}B" if x else "N/A")

# ── OUTPUT: ALL STOCKS RANKED ─────────────────────────────────────────────────
ranked = display.sort_values("Quality Score", ascending=False).drop(columns=["Passes"])
print("\n── All Stocks Ranked by Quality Score ──\n")
print(ranked[["Ticker", "Name", "Quality Score", "Gross Margin",
              "Revenue Growth", "ROE", "D/E Ratio", "P/E Ratio",
              "Market Cap ($B)"]].to_string(index=False))

# ── OUTPUT: STOCKS PASSING ALL FILTERS ───────────────────────────────────────
passing = display[display["Passes"] == True].sort_values("Quality Score", ascending=False)
print(f"\n── {len(passing)} stocks passed all quality filters ──\n")
if len(passing) > 0:
    print(passing[["Ticker", "Name", "Quality Score", "Gross Margin",
                   "Revenue Growth", "ROE", "D/E Ratio", "P/E Ratio",
                   "Market Cap ($B)"]].to_string(index=False))
else:
    print("  No stocks passed all filters. Try loosening the thresholds.")

print("\n── Screening complete ──\n")
