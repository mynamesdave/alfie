import streamlit as st
import yfinance as yf
import numpy as np
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Alfie: Covered Call Assistant", layout="centered")

st.title("🤖 Alfie: Your TSLA Covered Call Assistant")
st.markdown("Helps you pick high-probability covered call strikes based on historical volatility and current price.")

# User Inputs
st.sidebar.header("Settings")
lookback_days = st.sidebar.slider("Lookback period for volatility (days):", 10, 60, 20)
duration_days = st.sidebar.slider("Option duration (days):", 7, 30, 14)
std_dev_multiplier = st.sidebar.selectbox("Standard deviation multiplier:", [0.5, 1, 1.5, 2], index=1)
premium_input = st.sidebar.text_input("Premium per contract ($)", "")
contracts_input = st.sidebar.number_input("# of contracts (1 contract = 100 shares)", min_value=1, value=1)

# Fetch TSLA data
tsla = yf.Ticker("TSLA")
data = tsla.history(period=f"{lookback_days+5}d")  # Buffer to ensure clean data

# Calculate historical volatility
log_returns = np.log(data['Close'] / data['Close'].shift(1)).dropna()
hv = np.std(log_returns) * np.sqrt(252)  # Annualized HV

# Current price
current_price = data['Close'][-1]

# Projected move
base_sigma = hv * current_price * math.sqrt(duration_days / 252)
sigma = base_sigma * std_dev_multiplier
strike_price = math.ceil((current_price + sigma) / 5) * 5  # Round to nearest $5

# Display Outputs
st.subheader("📊 TSLA Snapshot")
st.write(f"**Current TSLA Price:** ${current_price:,.2f}")
st.write(f"**{lookback_days}-Day Historical Volatility (Annualized):** {hv:.2%}")
st.write(f"**Projected {duration_days}-Day +{std_dev_multiplier}σ Move:** +${sigma:,.2f}")
st.write(f"**📈 Suggested Covered Call Strike:** ${strike_price}")

# Optional: Yield and total premium Calculation
if premium_input.strip() != "":
    try:
        premium = float(premium_input)
        total_shares = contracts_input * 100
        total_premium = premium * contracts_input * 100
        yield_percent = (premium / current_price) * 100

        st.write(f"**💰 Estimated Yield per Contract:** {yield_percent:.2f}%")
        st.write(f"**📦 Total Premium (for {contracts_input} contract(s)):** ${total_premium:,.2f}")
    except:
        st.warning("Could not parse premium input. Please enter a number like 3.50")

# Bell Curve Visualization with 1σ, 2σ, 3σ lines
st.subheader("📉 Projected Price Distribution")
price_range = np.linspace(current_price - 3 * base_sigma, current_price + 3 * base_sigma, 300)
probability_density = (1 / (base_sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((price_range - current_price) / base_sigma) ** 2)

fig, ax = plt.subplots()
ax.plot(price_range, probability_density, label='Normal Distribution')
ax.axvline(current_price, color='green', linestyle='--', label='Current Price')
ax.axvline(strike_price, color='red', linestyle='--', label='Suggested Strike')

# Add 1σ, 2σ, 3σ lines
for i in [1, 2, 3]:
    ax.axvline(current_price + i * base_sigma, color='blue', linestyle=':', label=f'+{i}σ')
    ax.axvline(current_price - i * base_sigma, color='blue', linestyle=':', label=f'-{i}σ')

ax.fill_between(price_range, 0, probability_density, alpha=0.1)
ax.set_xlabel('Price')
ax.set_ylabel('Probability Density')
ax.set_title('Projected TSLA Price Distribution')
ax.legend()
st.pyplot(fig)

st.markdown("---")
st.caption("Built by Alfie to help you trade smarter. V1.1")
