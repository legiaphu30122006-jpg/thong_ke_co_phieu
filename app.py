import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vnstock3 import Vnstock
import time

# Cấu hình giao diện trang
st.set_page_config(page_title="Biểu đồ nến chứng khoán Real-time", layout="wide")
st.title("📈 Biểu đồ nến Chứng khoán Việt Nam (Real-time)")

# --- THANH CẤU HÌNH (SIDEBAR) ---
st.sidebar.header("Cấu hình dữ liệu")
symbol = st.sidebar.text_input("Mã chứng khoán", value="SSI").upper()
timeframe = st.sidebar.selectbox("Khung thời gian", options=["1D", "1H", "15m", "5m", "1m"], index=0)

st.sidebar.markdown("---")
st.sidebar.header("Cấu hình Tự động làm mới")
# Công tắc bật/tắt tính năng auto-refresh
auto_refresh = st.sidebar.checkbox("Bật tự động cập nhật", value=True)
# Lựa chọn số giây làm mới
refresh_interval = st.sidebar.slider("Khoảng thời gian cập nhật (giây)", min_value=5, max_value=60, value=10, step=5)

# Khởi tạo đối tượng vnstock
stock = Vnstock().stock(symbol=symbol, source="VCI")

# Hàm lấy dữ liệu (Không dùng cache để luôn lấy dữ liệu mới nhất từ API)
def load_data(ticker, resolution):
    df = stock.quote.history(
        symbol=ticker,
        start="2024-01-01",
        end="2025-09-07",
        interval=resolution
    )
    return df

# --- XỬ LÝ VÀ HIỂN THỊ BIỂU ĐỒ ---
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

        # Hiển thị thời gian cập nhật gần nhất trên tiêu đề biểu đồ
        current_time_str = time.strftime("%H:%M:%S - %d/%m/%Y")
        fig.update_layout(
            title=f"Biểu đồ giá {symbol} ({timeframe}) - Cập nhật lúc: {current_time_str}",
            yaxis_title="Giá (VND)",
            xaxis_title="Thời gian",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=600
        )

        # Hiển thị biểu đồ
        st.plotly_chart(fig, use_container_width=True)

        # Hiển thị bảng dữ liệu gần nhất
        with st.expander("Xem dữ liệu chi tiết gần nhất"):
            st.dataframe(df.tail(10))

    else:
        st.warning(f"Không tìm thấy dữ liệu cho mã {symbol}.")

except Exception as e:
    st.error(f"Có lỗi xảy ra khi tải dữ liệu: {e}")

# --- XỬ LÝ VÒNG LẶP TỰ ĐỘNG REFRESH ---
if auto_refresh:
    # Chờ N giây theo cài đặt người dùng
    time.sleep(refresh_interval)
    # Lệnh yêu cầu Streamlit chạy lại ứng dụng từ đầu để lấy dữ liệu mới
    st.rerun()
