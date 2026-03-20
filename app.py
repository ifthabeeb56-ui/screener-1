import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Nifty 500 Power Screener Pro", layout="wide")

# 10 മിനിറ്റിൽ ആപ്പ് തനിയെ പുതുക്കാൻ
st_autorefresh(interval=10 * 60 * 1000, key="nifty500refresh")

@st.cache_data
def get_nifty500_symbols():
    try:
        # Nifty 500 ലിസ്റ്റ് GitHub-ൽ നിന്ന് എടുക്കുന്നു
        url = "https://raw.githubusercontent.com/anirban-santra/Nifty-Indices-Stock-List/master/Nifty%20500.csv"
        df = pd.read_csv(url)
        symbols = [str(s) + ".NS" for s in df['Symbol'].tolist()]
        return symbols
    except:
        # ലിങ്ക് പരാജയപ്പെട്ടാൽ പകരമായി ഉപയോഗിക്കാൻ
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

# RSI കണക്കാക്കാനുള്ള ഫങ്ക്ഷൻ (തിരുത്തിയത്)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    # മുൻപ് തെറ്റിയ വരി ഇവിടെ തിരുത്തിയിട്ടുണ്ട് (1 + rs)
    return 100 - (100 / (1 + rs))

def run_power_screener():
    st.title("🚀 Advanced Trading Terminal (Nifty 500)")
    st.markdown("### സ്ട്രാറ്റജി: **EMA 20 > 50** & **RSI 40-65**")
    
    symbols = get_nifty500_symbols()
    
    if st.button("🔍 സ്കാൻ വിപണി (Scan Market)"):
        buy_signals = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # തുടക്കത്തിൽ ആദ്യത്തെ 100 സ്റ്റോക്കുകൾ സ്കാൻ ചെയ്യുന്നു (വേഗതയ്ക്ക് വേണ്ടി)
        target_stocks = symbols[:100] 

        for i, symbol in enumerate(target_stocks):
            try:
                status_text.text(f"പരിശോധിക്കുന്നു ({i+1}/{len(target_stocks)}): {symbol}")
                progress_bar.progress((i + 1) / len(target_stocks))
                
                # 8 മാസത്തെ ഡാറ്റ എടുക്കുന്നു
                df = yf.download(symbol, period='8mo', interval='1d', progress=False)
                
                if len(df) < 60: continue

                # Multi-index പ്രശ്നം ഒഴിവാക്കാൻ
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # EMA & RSI കണക്കാക്കുന്നു
                df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
                df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
                df['RSI'] = calculate_rsi(df['Close'])
                
                last_row = df.iloc[-1]
                
                # ഡാറ്റ കൃത്യമാണെന്ന് ഉറപ്പുവരുത്തുന്നു
                price = float(last_row['Close'])
                ema20 = float(last_row['EMA20'])
                ema50 = float(last_row['EMA50'])
                rsi_v = float(last_row['RSI'])

                # BUY കണ്ടീഷൻ
                if ema20 > ema50 and 40 < rsi_v < 65:
                    clean_name = symbol.replace(".NS", "")
                    buy_signals.append({
                        "Stock": clean_name,
                        "Price": round(price, 2),
                        "RSI": round(rsi_v, 2),
                        "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{clean_name}"
                    })
            except Exception as e:
                continue

        status_text.empty()
        progress_bar.empty()

        if buy_signals:
            st.success(f"✅ {len(buy_signals)} ബൈ സിഗ്നലുകൾ കണ്ടെത്തി!")
            res_df = pd.DataFrame(buy_signals)
            
            # ചാർട്ട് ലിങ്ക് ക്ലിക്കബിൾ ആക്കുന്നു
            res_df['Chart'] = res_df['Chart'].apply(lambda x: f'<a href="{x}" target="_blank">View 📈</a>')
            
            # റിസൾട്ട് കാണിക്കുന്നു
            st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # CSV ഡൗൺലോഡ് ബട്ടൺ
            csv = res_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 ഡൗൺലോഡ് CSV", data=csv, file_name='signals.csv', mime='text/csv')
        else:
            st.warning("നിലവിൽ ക്രൈറ്റീരിയ മാച്ച് ചെയ്യുന്ന സ്റ്റോക്കുകൾ ഇല്ല.")

if __name__ == "__main__":
    run_power_screener()
