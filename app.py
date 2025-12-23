import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="ETF Tracker", page_icon="📈")

st.title("📊 Taiwan ETF Tracker")

# --- 1. Currency Section (CAD to TWD) ---
st.subheader("💱 Exchange Rate")
try:
    # 'CADTWD=X' is the symbol for CAD to TWD exchange rate
    fx = yf.Ticker("CADTWD=X")
    fx_data = fx.history(period="2d") # Get 2 days to calculate change
    
    if not fx_data.empty:
        current_fx = fx_data['Close'].iloc[-1]
        prev_fx = fx_data['Close'].iloc[0]
        fx_change = current_fx - prev_fx
        
        # Display as a big metric
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
st.subheader("📉 Stock Watchlist (7% Buffer)")

etfs = ['00713.TW', '00919.TW', '0056.TW']

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
        target_price = low_52 * 1.07 # 7% buffer
        
        # Calculate percentage difference
        diff_percent = ((current_price - low_52) / low_52) * 100
        
        # Display Logic
        if current_price <= target_price:
             st.error(f"🚨 {ticker.replace('.TW','')} is in BUY ZONE!")
             st.metric(
                 label=ticker, 
                 value=f"${current_price:.2f}", 
                 delta=f"{diff_percent:.1f}% from low",
                 delta_color="inverse" # Red means 'good' (low price) in this context? Or just keep standard.
             )
             st.caption(f"Target was: ${target_price:.2f}")
        else:
             st.success(f"✅ {ticker.replace('.TW','')} is Safe")
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
  
