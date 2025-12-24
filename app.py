
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
    # 1. Get MAX History to find all-time records
    fx_ticker = "CADTWD=X"
    fx = yf.Ticker(fx_ticker)
    fx_hist = fx.history(period="max")
    
    if not fx_hist.empty:
        # Get Current Price
        curr_fx = fx_hist['Close'].iloc[-1]
        
        # Calculate 52-Week Low (Last 252 trading days approx 1 year)
        # We slice the last 252 rows for '1 Year' view
        last_year_data = fx_hist.tail(252)
        low_52 = last_year_data['Low'].min()
        
        # Calculate All-Time Low (Historical)
        low_all_time = fx_hist['Low'].min()
        
        # Calculate Target (based on 52-week low)
        target_fx = low_52 * (1 + BUFFER)
        
        # Calculate % differences
        diff_52 = ((curr_fx - low_52) / low_52) * 100
        diff_all = ((curr_fx - low_all_time) / low_all_time) * 100
        
        # ALERT LOGIC (Based on 52-week Low)
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
            
        # Display Details Table
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
        # 1. Get MAX History
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")
        
        if hist.empty:
            st.warning(f"No data for {ticker}")
            continue

        # 2. Calculate Metrics
        current_price = hist['Close'].iloc[-1]
        
        # 52-Week Data (Last 252 days)
        last_year_data = hist.tail(252)
        low_52 = last_year_data['Low'].min()
        
        # All-Time Data
        low_all_time = hist['Low'].min()
        
        # Target Price (5% buffer on 52-week low)
        target_price = low_52 * (1 + BUFFER)
        
        # Calculate % Gaps
        gap_52 = ((current_price - low_52) / low_52) * 100
        gap_all = ((current_price - low_all_time) / low_all_time) * 100
        
        clean_name = ticker.replace('.TW','')

        # 3. Logic: Is it near the 52-week low?
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
        
        # 4. Detailed Stats
        st.info(
            f"📉 **52-Week Low:** ${low_52:.2f}\n\n"
            f"🏛️ **All-Time Low:** ${low_all_time:.2f} (Gap: {gap_all:.2f}%)"
        )
             
        st.divider()
        
    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

# Refresh button
if st.button('Refresh Prices'):
    st.rerun()
    
