
import streamlit as st
import yfinance as yf
import time
import pandas as pd # Needed for the yield calculation

# --- Page Config ---
st.set_page_config(page_title="ETF & FX Tracker", page_icon="📈")

st.title("📊 Taiwan Market Tracker")
st.caption("Alerts trigger when price is within 5% of 52-Week Low")

# Define the buying buffer (5%)
BUFFER = 0.05 

# --- SMART CACHING FUNCTION ---
@st.cache_data(ttl=60)
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    # Get max history to calculate long-term yield
    hist = stock.history(period="max")
    return hist

# --- HELPER: CALCULATE AVG YIELD ---
def calculate_average_yield(hist):
    try:
        # 1. Create a copy to avoid modifying the cached data
        df = hist.copy()
        
        # 2. Ensure we have a Year column
        df['Year'] = df.index.year
        
        # 3. Group by Year: Sum dividends, Average the closing price
        yearly = df.groupby('Year').agg({
            'Dividends': 'sum', 
            'Close': 'mean'
        })
        
        # 4. Calculate Yield for each year
        yearly['Yield'] = yearly['Dividends'] / yearly['Close']
        
        # 5. Filter for years with actual dividends (> 0)
        valid_years = yearly[yearly['Yield'] > 0]
        
        # 6. Take the last 10 years (or fewer if less data exists)
        recent_years = valid_years.tail(10)
        
        if recent_years.empty:
            return 0.0, 0 # Return 0 if no dividend data
            
        avg_yield = recent_years['Yield'].mean() * 100 # Convert to percentage
        years_count = len(recent_years)
        
        return avg_yield, years_count
        
    except Exception as e:
        return 0.0, 0

st.divider()

# ==========================================
# SECTION 1: CAD to TWD CURRENCY
# ==========================================
st.subheader("💱 CAD/TWD Exchange Rate")

try:
    fx_hist = get_stock_data("CADTWD=X")
    
    if not fx_hist.empty:
        curr_fx = fx_hist['Close'].iloc[-1]
        
        # 52-Week Data
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
    st.warning(f"Currency unavailable (Rate Limit). Try again shortly.")

st.divider()

# ==========================================
# SECTION 2: ETF WATCHLIST
# ==========================================
st.subheader("📉 ETF Watchlist")

etfs = ['00713.TW', '00919.TW', '0056.TW', '0050.TW']

for ticker in etfs:
    try:
        hist = get_stock_data(ticker)
        
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
        
        # --- CALCULATE YIELD ---
        avg_yield, years_count = calculate_average_yield(hist)
        
        clean_name = ticker.replace('.TW','')

        # Alert Logic
        if current_price <= target_price:
             st.error(f"🚨 {clean_name} is in BUY ZONE!")
             st.metric(label=clean_name, value=f"${current_price:.2f}", delta=f"{gap_52:.2f}% from 52w Low", delta_color="inverse")
        else:
             st.success(f"✅ {clean_name} is Waiting")
             st.metric(label=clean_name, value=f"${current_price:.2f}", delta=f"+{gap_52:.2f}% from 52w Low")
        
        # Display Stats with Yield
        st.info(
            f"💰 **Avg Yield:** {avg_yield:.2f}% (Last {years_count} yrs)\n\n"
            f"📉 **52-Week Low:** ${low_52:.2f}\n\n"
            f"🏛️ **All-Time Low:** ${low_all_time:.2f} (Gap: {gap_all:.2f}%)"
        )
             
        st.divider()
        
    except Exception as e:
        st.warning(f"Loading {ticker}... (Rate Limit)")

# ==========================================
# SECTION 3: REFRESH
# ==========================================
st.caption("Auto-refresh checks every 60s.")
auto_refresh = st.checkbox("🔄 Enable Auto-Refresh")

if auto_refresh:
    time.sleep(60)
    st.rerun()

if st.button('Manual Refresh'):
    st.cache_data.clear()
    st.rerun()
    
