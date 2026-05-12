import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MNQ Trading Bias Dashboard", layout="wide")
st.title("📊 MNQ Intraday Bias Dashboard")

# 🔑 PASTE YOUR KEY STRING FROM ALPHAVANTAGE.CO HERE
API_KEY = "8KWHATUD8NSY4O1U"

# 1. Macro Indicators Section
st.header("🌐 Global Macro Sentiment")

@st.cache_data(ttl=300) # Caches the data for 5 minutes
def fetch_macro_data():
    # Corrected full URL schema prefix string
    url = f"alphavantage.co{API_KEY}"
    try:
        response = requests.get(url).json()
        if "data" in response and len(response["data"]) >= 2:
            latest_val = float(response["data"][0]["value"])
            prev_val = float(response["data"][1]["value"])
            return latest_val, (latest_val - prev_val)
    except:
        pass
    return None, None

curr_yield, yield_chg = fetch_macro_data()

if curr_yield:
    st.metric(label="US 10-Year Treasury Yield", value=f"{curr_yield:.2f}%", delta=f"{yield_chg:+.2f}%")
else:
    st.warning("Bond macro system data currently initializing or loading...")

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

@st.cache_data(ttl=300)
def fetch_stock_data():
    data_list = []
    green_count = 0
    red_count = 0
    
    for ticker, name in tech_tickers.items():
        # Corrected full URL schema prefix string
        url = f"alphavantage.co{ticker}&apikey={API_KEY}"
        try:
            res = requests.get(url).json()
            if "Global Quote" in res and res["Global Quote"]:
                quote = res["Global Quote"]
                price_now = float(quote.get("05. price", 0))
                pct_str = quote.get("10. change percent", "0%").replace("%", "")
                pct_change = float(pct_str) if pct_str is not None else 0.0
            else:
                price_now, pct_change = 0.0, 0.0
        except:
            price_now, pct_change = 0.0, 0.0

        if pct_change > 0:
            green_count += 1
        elif pct_change < 0:
            red_count += 1

        data_list.append({
            "Ticker": ticker,
            "Company": name,
            "Price": f"${price_now:.2f}",
            "Daily Change (%)": f"{pct_change:+.2f}%"
        })
    return pd.DataFrame(data_list), green_count, red_count

df, green_count, red_count = fetch_stock_data()
st.dataframe(df, use_container_width=True)

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
