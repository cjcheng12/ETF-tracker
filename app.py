import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="ETF Tracker", page_icon="📈")

st.title("📊 Taiwan ETF Tracker")

# --- 1. Currency Section (CAD to TWD) ---
st.subheader("💱 Exchange Rate")
try:
    # Get CAD to TWD data
    fx = yf.Ticker("CADTWD=X")
    fx_data = fx.history(period="5d")
    
    if not fx_data.empty:
        current_fx = fx_data['Close'].iloc[-1]
        prev_fx = fx_data['Close'].iloc[-2] # Compare to previous day
        fx_change = current_fx - prev_fx
        
        st.metric(
            label="🇨🇦 CAD ➔ 🇹🇼 TWD", 
            value=f"${current_fx:.2f}", 
            delta=f"{fx_change:.2f}"
        )
    else:
        st.warning("Could not load exchange rate.")
        
except Exception as e:
    st.error(f"Currency Error: {e}")

st.divider()

# --- 2. ETF Section ---
st.subheader("📉 Stock Watchlist (5% Zone)")

etfs = ['00713.TW', '00919.TW', '0056.TW']

# Define the buying buffer (5%)
BUFFER = 0.05 

for ticker in etfs:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        # Calculate Logic
        current_price = hist['Close'].iloc[-1]
        low_52 = hist['Low'].min()
        
        # Target is the Low + 5%
        target_price = low_52 * (1 + BUFFER) 
        
        # Calculate how far we are from the low (in %)
        diff_percent = ((current_price - low_52) / low_52) * 100
        
        # Display Logic
        if current_price <= target_price:
             # ALERT! (This is your visual notification)
             st.error(f"🚨 {ticker.replace('.TW','')} is in BUY ZONE!")
             st.metric(
                 label=ticker, 
                 value=f"${current_price:.2f}", 
                 delta=f"{diff_percent:.1f}% from low",
                 delta_color="inverse" 
             )
             st.caption(f"Target (<5%) was: ${target_price:.2f}")
        else:
             # Safe / Wait
             st.success(f"✅ {ticker.replace('.TW','')} is Waiting")
             st.metric(
                 label=ticker, 
                 value=f"${current_price:.2f}", 
                 delta=f"+{diff_percent:.1f}% from low"
             )
             
        st.divider()
        
    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

# Refresh button
if st.button('Refresh Data'):
    st.rerun()
    
