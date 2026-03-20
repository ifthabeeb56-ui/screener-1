import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Nifty 500 Power Screener", layout="wide")

# 10 മിനിറ്റ് ഓട്ടോ റിഫ്രഷ്
st_autorefresh(interval=10 * 60 * 1000, key="nifty500refresh")

@st.cache_data
def get_nifty500_symbols():
    try:
        url = "https://raw.githubusercontent.com/anirban-santra/Nifty-Indices-Stock-List/master/Nifty%20500.csv"
        df = pd.read_csv(url)
        symbols = [str(s) + ".NS" for s in df['Symbol'].tolist()]
        return symbols
    except:
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

# RSI കണക്കാക്കാനുള്ള ഫങ്ക്ഷൻ (തനിയെ നിർമ്മിച്ചത്)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1=rs))

def run_power_screener():
    st.title("🚀 Advanced Trading Terminal (Nifty 500)")
    st.markdown("### കണ്ടീഷൻ: **EMA 20 > 50** & **RSI 40-65**")
    
    symbols = get_nifty500_symbols()
    
    if st.button("🔍 സ്കാൻ വിപണി (Scan Market)"):
        buy_signals = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # വേഗതയ്ക്ക് വേണ്ടി ആദ്യത്തെ 100 എണ്ണം മാത്രം
        target_stocks = symbols[:100] 

        for i, symbol in enumerate(target_stocks):
            try:
                status_text.text(f"പരിശോധിക്കുന്നു: {symbol}")
                progress_bar.progress((i + 1) / len(target_stocks))
                
                df = yf.download(symbol, period='8mo', interval='1d', progress=False)
                
                if len(df) < 60: continue

                # Multi-index ക്ലീൻ ചെയ്യുന്നു
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # EMA കണക്കാക്കുന്നു (pandas-ta ഇല്ലാതെ)
                df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
                df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
                
                # RSI കണക്കാക്കുന്നു
                df['RSI'] = calculate_rsi(df['Close'])
                
                last_row = df.iloc[-1]
                
                price = float(last_row['Close'])
                ema20 = float(last_row['EMA20'])
                ema50 = float(last_row['EMA50'])
                rsi_v = float(last_row['RSI'])

                if ema20 > ema50 and 40 < rsi_v < 65:
                    clean_name = symbol.replace(".NS", "")
                    buy_signals.append({
                        "Stock": clean_name,
                        "Price": round(price, 2),
                        "RSI": round(rsi_v, 2),
                        "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{clean_name}"
                    })
            except:
                continue

        status_text.empty()
        progress_bar.empty()

        if buy_signals:
            st.success(f"✅ {len(buy_signals)} സിഗ്നലുകൾ കണ്ടെത്തി!")
            res_df = pd.DataFrame(buy_signals)
            res_df['Chart'] = res_df['Chart'].apply(lambda x: f'<a href="{x}" target="_blank">View 📈</a>')
            st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.warning("നിലവിൽ നിബന്ധനകൾ പാലിക്കുന്ന സ്റ്റോക്കുകൾ ഇല്ല.")

if __name__ == "__main__":
    run_power_screener()
