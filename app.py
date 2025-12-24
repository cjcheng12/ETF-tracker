
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
        curr_fx = fx_hist['Close'].iloc[-1]
        low_fx = fx_hist['Low'].min()
        target_fx = low_fx * (1 + BUFFER)
        
        # Calculate % difference
        fx_diff = ((curr_fx - low_fx) / low_fx) * 100
        
        # Display Logic
        if curr_fx <= target_fx:
            st.error(f"🚨 CAD is WEAK (Near Low)")
            st.metric(
                label="CAD ➔ TWD", 
                value=f"${curr_fx:.2f}", 
                delta=f"{fx_diff:.2f}% from low",
                delta_color="inverse"
            )
        else:
            st.success(f"✅ CAD is Stronger")
            st.metric(
                label="CAD ➔ TWD", 
                value=f"${curr_fx:.2f}", 
                delta=f"+{fx_diff:.2f}% from low"
            )
            
        # Explicitly show the lowest price
        st.info(f"📉 **52-Week Low:** ${low_fx:.2f} (Current is {fx_diff:.2f}% higher)")
            
    else:
        st.warning("Could not load currency data.")

except Exception as e:
    st.error(f"Currency Error: {e}")

st.divider()

# ==========================================
# SECTION 2: ETF WATCHLIST
# ==========================================
st.subheader("📉 ETF Watchlist")

# Added 0050.TW to the list
etfs = ['00713.TW', '00919.TW', '0056.TW', '0050.TW']

for ticker in etfs:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        # Calculate Metrics
        current_price = hist['Close'].iloc[-1]
        low_52 = hist['Low'].min()
        target_price = low_52 * (1 + BUFFER)
        
        # Calculate % difference
        diff_percent = ((current_price - low_52) / low_52) * 100
        
        # Clean Ticker Name (Remove .TW)
        clean_name = ticker.replace('.TW','')

        # Logic: Is it near the low?
        if current_price <= target_price:
             # ALERT ZONE
             st.error(f"🚨 {clean_name} is in BUY ZONE!")
             st.metric(
                 label=clean_name, 
                 value=f"${current_price:.2f}", 
                 delta=f"{diff_percent:.2f}% from low",
                 delta_color="inverse" 
             )
        else:
             # SAFE ZONE
             st.success(f"✅ {clean_name} is Waiting")
             st.metric(
                 label=clean_name, 
                 value=f"${current_price:.2f}", 
                 delta=f"+{diff_percent:.2f}% from low"
             )
        
        # Extra details you requested
        st.info(f"📉 **Lowest Price (52w):** ${low_52:.2f} | **Gap:** {diff_percent:.2f}%")
             
        st.divider()
        
    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

# Refresh button
if st.button('Refresh Prices'):
    st.rerun()
    
