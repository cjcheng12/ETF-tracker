import streamlit as st
import yfinance as yf
import time # Needed for the timer

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
    # 1. Get MAX History
    fx_ticker = "CADTWD=X"
    fx = yf.Ticker(fx_ticker)
    fx_hist = fx.history(period="max")
    
    if not fx_hist.empty:
        curr_fx = fx_hist['Close'].iloc[-1]
        
        # 52-Week Data (approx 252 trading days)
        last_year_data = fx_hist.tail(252)
        low_52 = last_year_data['Low'].min()
        
        # All-Time Data
        low_all_time = fx_hist['Low'].min()
        
        # Target
        target_fx = low_52 * (1 + BUFFER)
        
        # % Gaps
        diff_52 = ((curr_fx - low_52) / low_52) * 100
        diff_all = ((curr_fx - low_all_time) / low_all_time) * 100
        
        # ALERT LOGIC
        if curr_fx <= target_fx:
            st.error(f"🚨 CAD is WEAK (Near 52-Week Low)")
            st.metric(
                label="CAD ➔ TWD", 
                value=f"${curr_fx:.2f}", 
                delta=f"{diff_52:.2f}% from 52w low",
                delta_color="inverse"
            )
        else:
            st.success(f"✅ CAD is Stronger")
            st.metric(
                label="CAD ➔ TWD", 
                value=f"${curr_fx:.2f}", 
                delta=f"+{diff_52:.2f}% from 52w low"
            )
            
        st.write(f"📉 **52-Week Low:** ${low_52:.2f}")
        st.write(f"🏛️ **All-Time Low:** ${low_all_time:.2f} (Gap: {diff_all:.2f}%)")
            
    else:
        st.warning("Could not load currency data.")

except Exception as e:
    st.error(f"Currency Error: {e}")

st.divider()

# ==========================================
# SECTION 2: ETF WATCHLIST
# ==========================================
st.subheader("📉 ETF Watchlist")

etfs = ['00713.TW', '00919.TW', '0056.TW', '0050.TW']

for ticker in etfs:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")
        
        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        # Metrics
        current_price = hist['Close'].iloc[-1]
        last_year_data = hist.tail(252)
        low_52 = last_year_data['Low'].min()
        low_all_time = hist['Low'].min()
        
        target_price = low_52 * (1 + BUFFER)
        
        gap_52 = ((current_price - low_52) / low_52) * 100
        gap_all = ((current_price - low_all_time) / low_all_time) * 100
        
        clean_name = ticker.replace('.TW','')

        # Logic
        if current_price <= target_price:
             st.error(f"🚨 {clean_name} is in BUY ZONE!")
             st.metric(
                 label=clean_name, 
                 value=f"${current_price:.2f}", 
                 delta=f"{gap_52:.2f}% from 52w Low",
                 delta_color="inverse" 
             )
        else:
             st.success(f"✅ {clean_name} is Waiting")
             st.metric(
                 label=clean_name, 
                 value=f"${current_price:.2f}", 
                 delta=f"+{gap_52:.2f}% from 52w Low"
             )
        
        st.info(
            f"📉 **52-Week Low:** ${low_52:.2f}\n\n"
            f"🏛️ **All-Time Low:** ${low_all_time:.2f} (Gap: {gap_all:.2f}%)"
        )
             
        st.divider()
        
    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

# ==========================================
# SECTION 3: AUTO REFRESH
# ==========================================
# Checkbox to enable/disable auto-refresh
auto_refresh = st.checkbox("🔄 Enable Auto-Refresh (Every 10s)")

if auto_refresh:
    time.sleep(10) # Wait 10 seconds
    st.rerun()     # Reload the app

# Manual refresh button (always available)
if st.button('Manual Refresh Now'):
    st.rerun()
    
