
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="AI Trading Signal Bot",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Multi-Currency Trading Signal Bot")
st.warning(
    "Educational signals only. Not financial advice. "
    "Signals are not guaranteed to be profitable."
)

# Currency pairs
CURRENCY_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "USD/CHF": "CHF=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
}

pair = st.selectbox(
    "Select Currency Pair",
    list(CURRENCY_PAIRS.keys())
)

period = st.selectbox(
    "Select Chart Period",
    ["1d", "5d", "1mo", "3mo"],
    index=1
)

interval = st.selectbox(
    "Select Candle Interval",
    ["5m", "15m", "30m", "60m"],
    index=0
)

if st.button("Analyze Market"):
    with st.spinner("Fetching market data..."):
        try:
            ticker = CURRENCY_PAIRS[pair]
            data = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False
            )

            if data.empty or len(data) < 20:
                st.error(
                    "Not enough data. Try another period "
                    "or currency pair."
                )
            else:
                close = data["Close"]

                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                close = close.dropna()

                ema9 = close.ewm(span=9, adjust=False).mean()
                ema21 = close.ewm(span=21, adjust=False).mean()
                latest = float(close.iloc[-1])

                st.metric("Currency Pair", pair)
                st.metric("Latest Available Price", f"{latest:.5f}")

                if ema9.iloc[-1] > ema21.iloc[-1]:
                    st.success("UP BIAS 📈")
                    st.write(
                        "Short-term trend is above the longer EMA. "
                        "This is not a confirmed trade entry."
                    )
                elif ema9.iloc[-1] < ema21.iloc[-1]:
                    st.error("DOWN BIAS 📉")
                    st.write(
                        "Short-term trend is below the longer EMA. "
                        "This is not a confirmed trade entry."
                    )
                else:
                    st.info("NEUTRAL — No clear trend.")

                chart = pd.DataFrame({
                    "Close": close,
                    "EMA 9": ema9,
                    "EMA 21": ema21
                })

                st.line_chart(chart)
                st.caption(
                    "Data may be delayed or unavailable. "
                    "Yahoo Finance prices may differ from Pocket Option."
                )

        except Exception as e:
            st.error(f"Could not analyze market: {e}")
