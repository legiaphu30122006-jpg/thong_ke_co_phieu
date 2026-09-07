import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vnstock3 import Vnstock

# Cấu hình giao diện trang
st.set_page_config(page_title="Biểu đồ nến chứng khoán", layout="wide")
st.title("📈 Biểu đồ nến Chứng khoán Việt Nam (vnstock)")

# Thanh điều hướng bên trái
st.sidebar.header("Cấu hình")
symbol = st.sidebar.text_input("Mã chứng khoán", value="SSI").upper()
timeframe = st.sidebar.selectbox("Khung thời gian", options=["1D", "1H", "15m", "5m"], index=0)

# Khởi tạo vnstock
stock = Vnstock().stock(symbol=symbol, source="VCI")

@st.cache_data(ttl=60)
def load_data(ticker, resolution):
    df = stock.quote.history(
        symbol=ticker,
        start="2024-01-01",
        end="2025-09-07",
        interval=resolution
    )
    return df

try:
    df = load_data(symbol, timeframe)

    if df is not None and not df.empty:
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
        
        # Vẽ biểu đồ nến Plotly
        fig = go.Figure(data=[go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )])

        fig.update_layout(
            title=f"Biểu đồ giá {symbol} ({timeframe}) - Cập nhật đến 07/09/2025",
            yaxis_title="Giá (VND)",
            xaxis_title="Thời gian",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Xem dữ liệu chi tiết"):
            st.dataframe(df.tail(10))

    else:
        st.warning(f"Không tìm thấy dữ liệu cho mã {symbol}.")

except Exception as e:
    st.error(f"Có lỗi xảy ra: {e}")
