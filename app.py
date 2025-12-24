import streamlit as st
import yfinance as yf
import time

# --- Page Config ---
st.set_page_config(page_title="ETF & FX Tracker", page_icon="📈")

st.title("📊 Taiwan Market Tracker")
st.caption("Alerts trigger when price is within 5% of 52-Week Low")

# Define the buying buffer (5%)
BUFFER = 0.05 

# --- SMART CACHING FUNCTION (The Fix) ---
# This prevents "Too Many Requests" errors by remembering data for 60 seconds
@st.cache_data(ttl=60)
def get_stock_history(symbol):
    stock = yf.Ticker(symbol)
    # return the full history
    return stock.history(period="max")

st.divider()

# ==========================================
# SECTION 1: CAD to TWD CURRENCY
# ==========================================
st.subheader("💱 CAD/TWD Exchange Rate")

try:
    # Use the cached function instead of calling yfinance directly
    fx_hist = get_stock_history("CADTWD=X")
    
    if not fx_hist.empty:
        curr_fx = fx_hist['Close'].iloc[-1]
        
        # 52-Week Data (approx 252 trading days)
        last_year_data = fx_hist.tail(252)
        low_52 = last_year_data['Low'].min()
        low_all_time = fx_hist['Low'].min()
        
        target_fx = low_52 * (1 + BUFFER)
        
        diff_52 = ((curr_fx - low_52) / low_52) * 100
        diff_all = ((curr_fx - low_all_time) / low_all_time) * 100
        
        if curr_fx <= target_fx:
            st.error(f"🚨 CAD is WEAK (Near 52-Week Low)")
            st.metric(label="CAD ➔ TWD", value=f"${curr_fx:.2f}", delta=f"{diff_52:.2f}% from 52w low", delta_color="inverse")
        else:
            st.success(f"✅ CAD is Stronger")
            st.metric(label="CAD ➔ TWD", value=f"${curr_fx:.2f}", delta=f"+{diff_52:.2f}% from 52w low")
            
        st.write(f"📉 **52-Week Low:** ${low_52:.2f}")
        st.write(f"🏛️ **All-Time Low:** ${low_all_time:.2f} (Gap: {diff_all:.2f}%)")
    else:
        st.warning("Could not load currency data.")

except Exception as e:
    st.warning(f"Currency currently unavailable (Rate Limit). Try again in 1 min.")

st.divider()

# ==========================================
# SECTION 2: ETF WATCHLIST
# ==========================================
st.subheader("📉 ETF Watchlist")

etfs = ['00713.TW', '00919.TW', '0056.TW', '0050.TW']

for ticker in etfs:
    try:
        # Use the cached function
        hist = get_stock_history(ticker)
        
        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        current_price = hist['Close'].iloc[-1]
        last_year_data = hist.tail(252)
        low_52 = last_year_data['Low'].min()
        low_all_time = hist['Low'].min()
        
        target_price = low_52 * (1 + BUFFER)
        
        gap_52 = ((current_price - low_52) / low_52) * 100
        gap_all = ((current_price - low_all_time) / low_all_time) * 100
        
        clean_name = ticker.replace('.TW','')

        if current_price <= target_price:
             st.error(f"🚨 {clean_name} is in BUY ZONE!")
             st.metric(label=clean_name, value=f"${current_price:.2f}", delta=f"{gap_52:.2f}% from 52w Low", delta_color="inverse")
        else:
             st.success(f"✅ {clean_name} is Waiting")
             st.metric(label=clean_name, value=f"${current_price:.2f}", delta=f"+{gap_52:.2f}% from 52w Low")
        
        st.info(f"📉 **52-Week Low:** ${low_52:.2f}\n\n🏛️ **All-Time Low:** ${low_all_time:.2f} (Gap: {gap_all:.2f}%)")
             
        st.divider()
        
    except Exception as e:
        st.warning(f"Could not load {ticker}. (Rate Limit hit - wait a moment)")

# ==========================================
# SECTION 3: SAFER REFRESH
# ==========================================
st.caption("Auto-refresh checks every 60s to prevent blocking.")
auto_refresh = st.checkbox("🔄 Enable Auto-Refresh")

if auto_refresh:
    time.sleep(60) # Increased to 60s to prevent errors
    st.rerun()

if st.button('Manual Refresh'):
    st.cache_data.clear() # This forces a real update when you click the button
    st.rerun()

