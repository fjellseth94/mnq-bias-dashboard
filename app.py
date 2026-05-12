import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MNQ Trading Bias Dashboard", layout="wide")
st.title("📊 MNQ Intraday Bias Dashboard")

# 1. Macro Indicators Section
st.header("🌐 Global Macro Sentiment")
bond = yf.Ticker("^TNX") 
bond_hist = bond.history(period="2d")

if len(bond_hist) >= 2:
    prev_close = bond_hist['Close'].iloc[-2]
    curr_yield = bond_hist['Close'].iloc[-1]
    yield_chg = curr_yield - prev_close
    st.metric(label="US 10-Year Treasury Yield", value=f"{curr_yield:.2f}%", delta=f"{yield_chg:+.2f}%")
else:
    st.warning("Bond data temporarily unavailable.")

# 2. Big Tech Watchlist Section
st.header("🍏 Big Tech Market Weight (Nasdaq-100 Drivers)")

tech_tickers = {
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "NVDA": "Nvidia",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet",
    "META": "Meta Platforms"
}

data_list = []
green_count = 0
red_count = 0

for ticker, name in tech_tickers.items():
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")
    
    if len(hist) >= 2:
        close_yesterday = hist['Close'].iloc[-2]
        price_now = hist['Close'].iloc[-1]
        pct_change = ((price_now - close_yesterday) / close_yesterday) * 100
    else:
        price_now, pct_change = 0.0, 0.0

    if pct_change > 0:
        green_count += 1
    elif pct_change < 0:
        red_count += 1

    data_list.append({
        "Ticker": ticker,
        "Company": name,
        "Price": f"${price_now:.2f}",
        "Daily Change (%)": f"{pct_change:+.2f}%",
        "Raw_Chg": pct_change
    })

df = pd.DataFrame(data_list)
st.dataframe(df[["Ticker", "Company", "Price", "Daily Change (%)"]], use_container_width=True)

# 3. Market Bias System Execution Output
st.header("⚡ Intraday MNQ Directional Bias")
if green_count == 6:
    st.success("🟢 STRONGLY BULLISH: All 6 Tech giants are green. Focus strictly on MNQ long setups.")
elif red_count == 6:
    st.error("🔴 STRONGLY BEARISH: All 6 Tech giants are red. Focus strictly on MNQ short setups.")
elif green_count >= 4:
    st.info("🟡 MILDLY BULLISH: Tech heavily favors upside. Look for long entries at support.")
elif red_count >= 4:
    st.info("🟡 MILDLY BEARISH: Tech heavily favors downside. Look for short entries at resistance.")
else:
    st.warning("⚪ CHOPPY / RANGE-BOUND: Mixed market signals. Scalp the ranges or stand aside.")
