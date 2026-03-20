import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Custom Power Screener", layout="wide")
st_autorefresh(interval=10 * 60 * 1000, key="nifty500refresh")

@st.cache_data
def get_nifty500_symbols():
    try:
        url = "https://raw.githubusercontent.com/anirban-santra/Nifty-Indices-Stock-List/master/Nifty%20500.csv"
        df = pd.read_csv(url)
        return [str(s) + ".NS" for s in df['Symbol'].tolist()]
    except:
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# സൈഡ് ബാറിൽ സെറ്റിംഗ്സ് സെറ്റ് ചെയ്യുന്നു
st.sidebar.header("⚙️ സ്കാനർ സെറ്റിംഗ്സ്")
ema_short = st.sidebar.slider("Short EMA (ഉദാ: 20)", 5, 50, 20)
ema_long = st.sidebar.slider("Long EMA (ഉദാ: 50)", 20, 200, 50)
rsi_min = st.sidebar.slider("RSI മിനിമം", 10, 50, 40)
rsi_max = st.sidebar.slider("RSI മാക്സിമം", 50, 90, 65)

def run_power_screener():
    st.title("🚀 Advanced Trading Terminal (Nifty 500)")
    st.markdown(f"**നിലവിലെ കണ്ടീഷൻ:** EMA {ema_short} > {ema_long} | RSI {rsi_min} നും {rsi_max} നും ഇടയിൽ")
    
    symbols = get_nifty500_symbols()
    
    if st.button("🔍 സ്കാൻ വിപണി (Scan Market)"):
        buy_signals = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        target_stocks = symbols[:100] # ആദ്യത്തെ 100 എണ്ണം

        for i, symbol in enumerate(target_stocks):
            try:
                status_text.text(f"പരിശോധിക്കുന്നു: {symbol}")
                progress_bar.progress((i + 1) / len(target_stocks))
                
                df = yf.download(symbol, period='1y', interval='1d', progress=False)
                if len(df) < ema_long + 10: continue

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # സ്ലൈഡറിൽ നിന്നുള്ള വാല്യൂസ് ഉപയോഗിക്കുന്നു
                df['EMA_S'] = df['Close'].ewm(span=ema_short, adjust=False).mean()
                df['EMA_L'] = df['Close'].ewm(span=ema_long, adjust=False).mean()
                df['RSI'] = calculate_rsi(df['Close'])
                
                last_row = df.iloc[-1]
                
                price = float(last_row['Close'])
                e_s = float(last_row['EMA_S'])
                e_l = float(last_row['EMA_L'])
                rsi_v = float(last_row['RSI'])

                if e_s > e_l and rsi_min < rsi_v < rsi_max:
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
            st.warning("ഈ ക്രൈറ്റീരിയയിൽ സ്റ്റോക്കുകൾ ഒന്നുമില്ല. സെറ്റിംഗ്സ് മാറ്റി പരീക്ഷിക്കൂ.")

if __name__ == "__main__":
    run_power_screener()
