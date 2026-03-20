import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(page_title="Smart Stock Screener", layout="wide")

st.title("📈 Advanced Trading Terminal")
st.markdown("EMA Crossover & RSI Analysis (Nifty Stocks)")

# ടിക്കറുകൾ (നിങ്ങൾക്ക് ഇഷ്ടമുള്ളവ ഇവിടെ ആഡ് ചെയ്യാം)
tickers = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "SBIN", "BHARTIARTL"]
formatted_tickers = [t + ".NS" for t in tickers]

if st.button("🔍 സ്കാൻ വിപണി (Scan Market)"):
    with st.spinner('ഡാറ്റ വിശകലനം ചെയ്യുന്നു...'):
        try:
            # ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു (Group by Ticker for better handling)
            all_data = yf.download(formatted_tickers, period="1y", interval="1d", group_by='ticker', progress=False)
            
            for ticker in tickers:
                ticker_ns = ticker + ".NS"
                df = all_data[ticker_ns].copy().dropna()
                
                if len(df) > 50:
                    # Indicators കണക്കാക്കുന്നു
                    df['EMA20'] = ta.ema(df['Close'], length=20)
                    df['EMA50'] = ta.ema(df['Close'], length=50)
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    
                    curr = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    # സിഗ്നൽ ലോജിക്
                    is_golden = (prev['EMA20'] <= prev['EMA50']) and (curr['EMA20'] > curr['EMA50'])
                    is_death = (prev['EMA20'] >= prev['EMA50']) and (curr['EMA20'] < curr['EMA50'])
                    
                    if is_golden:
                        status, color = "🔥 GOLDEN CROSS (BUY)", "#ffff00"
                    elif is_death:
                        status, color = "💀 DEATH CROSS (SELL)", "#ff4b4b"
                    elif curr['EMA20'] > curr['EMA50']:
                        status, color = "Bullish 📈", "#00ff00"
                    else:
                        status, color = "Bearish 📉", "#ff4b4b"

                    # --- ഡിസ്പ്ലേ സെക്ഷൻ ---
                    with st.expander(f"{ticker} - {status} (Price: ₹{round(curr['Close'], 2)})"):
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            st.metric("Price", f"₹{round(curr['Close'], 2)}")
                            st.metric("RSI", round(curr['RSI'], 2))
                            if curr['RSI'] > 70: st.warning("Overbought ⚠️")
                            if curr['RSI'] < 30: st.info("Oversold 💎")

                        with col2:
                            # Plotly Candlestick Chart
                            fig = go.Figure()
                            fig.add_trace(go.Candlestick(x=df.index[-60:], open=df['Open'], high=df['High'], 
                                                        low=df['Low'], close=df['Close'], name='Price'))
                            fig.add_trace(go.Scatter(x=df.index[-60:], y=df['EMA20'][-60:], name='EMA 20', line=dict(color='blue')))
                            fig.add_trace(go.Scatter(x=df.index[-60:], y=df['EMA50'][-60:], name='EMA 50', line=dict(color='orange')))
                            
                            fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)

            st.success("സ്കാനിംഗ് വിജയകരമായി പൂർത്തിയായി!")
            
        except Exception as e:
            st.error(f"Error: {e}")

st.info("💡 Tip: Golden Cross വന്നാൽ RSI 50-70 റേഞ്ചിലാണോ എന്ന് നോക്കുന്നത് കൂടുതൽ സുരക്ഷിതമാണ്.")
