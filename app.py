import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Nifty 500 Power Screener", layout="wide")

# ഓട്ടോ റിഫ്രഷ് (ഓരോ 10 മിനിറ്റിലും)
st_autorefresh(interval=10 * 60 * 1000, key="nifty500refresh")

@st.cache_data
def get_nifty500_symbols():
    try:
        # Nifty 500 ലിസ്റ്റ് GitHub-ൽ നിന്ന് നേരിട്ട് എടുക്കുന്നു
        url = "https://raw.githubusercontent.com/anirban-santra/Nifty-Indices-Stock-List/master/Nifty%20500.csv"
        df = pd.read_csv(url)
        # yfinance-ന് വേണ്ടി .NS ചേർക്കുന്നു
        symbols = [str(s) + ".NS" for s in df['Symbol'].tolist()]
        return symbols
    except:
        # ലിങ്ക് വർക്ക് ചെയ്യുന്നില്ലെങ്കിൽ മാത്രം ഉപയോഗിക്കാൻ ബാക്കപ്പ്
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

def run_power_screener():
    st.title("🚀 Nifty 500 Advanced Trading Terminal")
    
    # ഫോട്ടോയിലെ എറർ വരാതിരിക്കാൻ unsafe_allow_html ആണ് ഉപയോഗിക്കേണ്ടത്
    st.markdown("### കണ്ടീഷൻ: **EMA 20 > 50** & **RSI 40-65**")
    
    symbols = get_nifty500_symbols()
    
    # സ്കാൻ ബട്ടൺ
    if st.button("🔍 സ്കാൻ വിപണി (Scan Market)"):
        buy_signals = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # തുടക്കത്തിൽ ആദ്യത്തെ 100 എണ്ണം സ്കാൻ ചെയ്യാൻ വെക്കുന്നു (വേഗതയ്ക്ക് വേണ്ടി)
        # മുഴുവൻ വേണമെങ്കിൽ symbols[:100] എന്നത് symbols എന്ന് മാത്രമാക്കുക
        target_stocks = symbols[:100] 

        for i, symbol in enumerate(target_stocks):
            try:
                status_text.text(f"പരിശോധിക്കുന്നു ({i+1}/{len(target_stocks)}): {symbol}")
                progress_bar.progress((i + 1) / len(target_stocks))
                
                df = yf.download(symbol, period='6mo', interval='1d', progress=False)
                
                if len(df) < 50: continue

                # കോളം നെയിം ക്ലീൻ ചെയ്യുന്നു
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df['EMA20'] = ta.ema(df['Close'], length=20)
                df['EMA50'] = ta.ema(df['Close'], length=50)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                
                last_row = df.iloc[-1]
                
                # വാല്യൂസ് എടുക്കുന്നു
                close_p = float(last_row['Close'])
                ema20 = float(last_row['EMA20'])
                ema50 = float(last_row['EMA50'])
                rsi_v = float(last_row['RSI'])

                if ema20 > ema50 and 40 < rsi_v < 65:
                    clean_name = symbol.replace(".NS", "")
                    buy_signals.append({
                        "Stock": clean_name,
                        "Price": round(close_p, 2),
                        "RSI": round(rsi_v, 2),
                        "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{clean_name}"
                    })
            except:
                continue

        status_text.empty()
        progress_bar.empty()

        if buy_signals:
            st.success(f"✅ {len(buy_signals)} ബൈ സിഗ്നലുകൾ കണ്ടെത്തി!")
            res_df = pd.DataFrame(buy_signals)
            
            # TradingView ലിങ്ക് ക്ലിക്കബിൾ ആക്കുന്നു
            res_df['Chart'] = res_df['Chart'].apply(lambda x: f'<a href="{x}" target="_blank">View 📈</a>')
            
            # ഡിസ്പ്ലേ
            st.write(res_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.warning("നിലവിൽ നിബന്ധനകൾ പാലിക്കുന്ന സ്റ്റോക്കുകൾ ഇല്ല.")

if __name__ == "__main__":
    run_power_screener()
