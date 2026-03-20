import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- Header ---
st.set_page_config(page_title="Pro Stock Screener", layout="wide")
st.subheader("🚀 Advanced Trading Terminal (EMA + RSI)")

# Tickers List
tickers = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "TATAMOTORS", "SBI", "BHARTIARTL"]
formatted_tickers = [t + ".NS" for t in tickers]

if st.button("🔍 സ്കാൻ വിപണി (Scan Market)"):
    with st.spinner('ഡാറ്റ വിശകലനം ചെയ്യുന്നു...'):
        try:
            # Download Data
            all_data = yf.download(formatted_tickers, period="1y", interval="1d", group_by='ticker', progress=False)
            
            trend_results = []
            
            for ticker in tickers:
                ticker_ns = ticker + ".NS"
                if ticker_ns in all_data:
                    prices = all_data[ticker_ns]['Close'].dropna()
                    
                    if len(prices) > 50:
                        # EMA Calculation (Manual)
                        ema20 = prices.ewm(span=20, adjust=False).mean()
                        ema50 = prices.ewm(span=50, adjust=False).mean()
                        
                        # RSI Calculation (Manual)
                        delta = prices.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        
                        curr_ema20, prev_ema20 = ema20.iloc[-1], ema20.iloc[-2]
                        curr_ema50, prev_ema50 = ema50.iloc[-1], ema50.iloc[-2]
                        curr_rsi = rsi.iloc[-1]
                        curr_price = prices.iloc[-1]
                        
                        # Signal Logic
                        is_golden_cross = (prev_ema20 <= prev_ema50) and (curr_ema20 > curr_ema50)
                        is_death_cross = (prev_ema20 >= prev_ema50) and (curr_ema20 < curr_ema50)
                        
                        if is_golden_cross:
                            status, color = "🔥 GOLDEN CROSS", "#ffff00"
                        elif is_death_cross:
                            status, color = "💀 DEATH CROSS", "#ff4b4b"
                        elif curr_ema20 > curr_ema50:
                            status, color = "Bullish 📈", "#00ff00"
                        else:
                            status, color = "Bearish 📉", "#ff4b4b"

                        trend_results.append({
                            "Stock": ticker, "Price": round(curr_price, 2),
                            "RSI": round(curr_rsi, 2), "Signal": status, "color": color
                        })
            
            # Visual Cards
            if trend_results:
                cols = st.columns(3)
                for idx, res in enumerate(trend_results):
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div style="background-color:#1e2130; padding:15px; border-radius:10px; border-left: 5px solid {res['color']}; margin-bottom:10px;">
                                <h4 style="margin:0; color:white;">{res['Stock']}</h4>
                                <p style="margin:0; color:#b0b0b0;">Price: <b>₹{res['Price']}</b></p>
                                <p style="margin:5px 0; color:{res['color']}; font-weight:bold;">{res['Signal']}</p>
                                <p style="margin:0; color:#888; font-size:12px;">RSI: {res['RSI']}</p>
                            </div>
                        """, unsafe_allow_code=True)
                st.success("സ്കാനിംഗ് വിജയകരമായി പൂർത്തിയായി!")
            
        except Exception as e:
            st.error(f"Error: {e}")

st.info("💡 സൂചന: Golden Cross വന്നാൽ വാങ്ങുന്നതിന് മുൻപ് RSI 70-ന് താഴെയാണോ എന്ന് ഉറപ്പുവരുത്തുക.")
