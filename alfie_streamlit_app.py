import streamlit as st
import yfinance as yf
import numpy as np
import math

st.set_page_config(page_title="Alfie: Covered Call Assistant", layout="centered")

st.title("🤖 Alfie: Your TSLA Covered Call Assistant")
st.markdown("Helps you pick high-probability covered call strikes based on historical volatility and current price.")

# User Inputs
st.sidebar.header("Settings")
lookback_days = st.sidebar.slider("Lookback period for volatility (days):", 10, 60, 20)
duration_days = st.sidebar.slider("Option duration (days):", 7, 30, 14)
std_dev_multiplier = st.sidebar.selectbox("Standard deviation multiplier:", [0.5, 1, 1.5, 2], index=1)
premium_input = st.sidebar.text_input("Optional: Premium you'd collect ($)", "")

# Fetch TSLA data
tsla = yf.Ticker("TSLA")
data = tsla.history(period=f"{lookback_days+5}d")  # Buffer to ensure clean data

# Calculate historical volatility
log_returns = np.log(data['Close'] / data['Close'].shift(1)).dropna()
hv = np.std(log_returns) * np.sqrt(252)  # Annualized HV

# Current price
current_price = data['Close'][-1]

# Projected move
sigma = hv * current_price * math.sqrt(duration_days / 252) * std_dev_multiplier
strike_price = math.ceil((current_price + sigma) / 5) * 5  # Round to nearest $5

# Display Outputs
st.subheader("📊 TSLA Snapshot")
st.write(f"**Current TSLA Price:** ${current_price:,.2f}")
st.write(f"**{lookback_days}-Day Historical Volatility (Annualized):** {hv:.2%}")
st.write(f"**Projected {duration_days}-Day +{std_dev_multiplier}σ Move:** +${sigma:,.2f}")
st.write(f"**📈 Suggested Covered Call Strike:** ${strike_price}")

# Optional: Yield Calculation
if premium_input.strip() != "":
    try:
        premium = float(premium_input)
        yield_percent = (premium / current_price) * 100
        st.write(f"**💰 Estimated Yield from Premium:** {yield_percent:.2f}%")
    except:
        st.warning("Could not parse premium input. Please enter a number like 3.50")

st.markdown("---")
st.caption("Built by Alfie to help you trade smarter. V1.0")
