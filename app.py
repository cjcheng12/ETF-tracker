import streamlit as st
import yfinance as yf

# --- Page Config ---
st.set_page_config(page_title="ETF & FX Tracker", page_icon="📈")

st.title("📊 Taiwan Market Tracker")
st.caption("Alerts trigger when price is within 5% of 52-Week Low")

# Define the buying buffer (5%)
BUFFER = 0.05 

st.divider()

# ==========================================
# SECTION 1: CAD to TWD CURRENCY
# ==========================================
st.subheader("💱 CAD/TWD Exchange Rate")

try:
    # 1. Get 1 Year of Currency Data
    fx_ticker = "CADTWD=X"
    fx = yf.Ticker(fx_ticker)
    fx_hist = fx.history(period="1y")
    
    if not fx_hist.empty:
        # 2. Calculate Metrics
        curr_fx = fx_hist['Close'].iloc[-1]
        low_fx = fx_hist['Low'].min()
        high_fx = fx_hist['High'].max()
        target_fx = low_fx * (1 + BUFFER) # The "Alert" Price
        
        # Calculate % difference from low
        fx_diff = ((curr_fx - low_fx) / low_fx) * 100
        
        # 3. Logic: Is it near the low?
        if curr_fx <= target_fx:
            st.error(f"🚨 CAD is WEAK (Near 52-Week Low)")
            st.metric(
                label="CAD ➔ TWD", 
                value=f"${curr_fx:.2f}", 
                delta=f"{fx_diff:.2f}% from low",
                delta_color="inverse"
            )
            st.write(f"📉 **52-Week Low:** {low_fx:.2f}")
            st.write(f"⚠️ **Alert Zone (<{BUFFER*100:.0f}%):** {target_fx:.2f}")
            
        else:
            st.success(f"✅ CAD is Stronger")
            st.metric(
                label="CAD ➔ TWD", 
                value=f"${curr_fx:.2f}", 
                delta=f"+{fx_diff:.2f}% from low"
            )
            st.caption(f"Current rate is healthy (Low was {low_fx:.2f})")
            
    else:
        st.warning("Could not load currency data.")

except Exception as e:
    st.error(f"Currency Error: {e}")

st.divider()

# ==========================================
# SECTION 2: ETF WATCHLIST
# ==========================================
st.subheader("📉 ETF Watchlist")

etfs = ['00713.TW', '00919.TW', '0056.TW']

for ticker in etfs:
    try:
        # 1. Get 1 Year of Stock Data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        # 2. Calculate Metrics
        current_price = hist['Close'].iloc[-1]
        low_52 = hist['Low'].min()
        target_price = low_52 * (1 + BUFFER) # The "Alert" Price
        
        diff_percent = ((current_price - low_52) / low_52) * 100
        
        # 3. Logic: Is it near the low?
        if current_price <= target_price:
             # ALERT ZONE
             st.error(f"🚨 {ticker.replace('.TW','')} is in BUY ZONE!")
             st.metric(
                 label=ticker, 
                 value=f"${current_price:.2f}", 
                 delta=f"{diff_percent:.1f}% from low",
                 delta_color="inverse" 
             )
             st.write(f"📉 **Low:** {low_52:.2f} | 🎯 **Target:** <{target_price:.2f}")
        else:
             # SAFE ZONE
             st.success(f"✅ {ticker.replace('.TW','')} is Waiting")
             st.metric(
                 label=ticker, 
                 value=f"${current_price:.2f}", 
                 delta=f"+{diff_percent:.1f}% from low"
             )
             
        st.divider()
        
    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

# Refresh button at the bottom
if st.button('Refresh Prices'):
    st.rerun()
    
