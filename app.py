import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="MNQ Trading Bias Dashboard", layout="wide")
st.title("📊 MNQ Intraday Bias Dashboard")

# 🔄 AUTOMATIC REFRESH LOOP (Every 60 Seconds)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# 🔑 PASTE YOUR FREE FINNHUB API KEY HERE
API_KEY = "d81g1c9r01qler4i6qkgd81g1c9r01qler4i6ql0"

# 1. Macro Indicators Section
st.header("🌐 Global Macro Sentiment")

@st.cache_data(ttl=60)
def fetch_macro_data():
    # Fetching US 10-Year Treasury Yield via Finnhub indices tracking
    url = f"finnhub.io^TNX&token={API_KEY}"
    try:
        res = requests.get(url).json()
        if "c" in res and res["c"] != 0:
            price_now = float(res["c"])
            prev_close = float(res["pc"])
            pct_change = ((price_now - prev_close) / prev_close) * 100
            return price_now, pct_change
    except Exception:
        pass
    return None, None

curr_yield, yield_chg = fetch_macro_data()

if curr_yield is not None:
    st.metric(label="US 10-Year Treasury Yield", value=f"{curr_yield:.2f}%", delta=f"{yield_chg:+.2f}%")
else:
    st.warning("Bond macro data initializing or loading...")

# 2. Big Tech Watchlist Section
st.header("🍏 Big Tech Market Weight (Nasdaq-100 Drivers)")

tech_tickers = {
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "NVDA": "Nvidia",
    "AMZN": "Amazon",
    "GOOG": "Alphabet",
    "META": "Meta Platforms"
}

@st.cache_data(ttl=60)
def fetch_stock_data():
    data_list = []
    green_count = 0
    red_count = 0
    
    for ticker, name in tech_tickers.items():
        url = f"finnhub.io{ticker}&token={API_KEY}"
        try:
            res = requests.get(url).json()
            if "c" in res and res["c"] != 0:
                price_now = float(res["c"])
                prev_close = float(res["pc"])
                pct_change = ((price_now - prev_close) / prev_close) * 100
            else:
                price_now, pct_change = 0.0, 0.0
        except Exception:
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
            "raw_pct": pct_change
        })
    return pd.DataFrame(data_list), green_count, red_count

df, green_count, red_count = fetch_stock_data()

# Render table layout without the annoying left-side index numbers (0, 1, 2...)
if not df.empty:
    st.dataframe(df[["Ticker", "Company", "Price", "Daily Change (%)"]], use_container_width=True, hide_index=True)
else:
    st.error("Market data feed unavailable.")

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

# 🔄 Background continuous 60-second page rerun loop
time.sleep(60)
st.rerun()
