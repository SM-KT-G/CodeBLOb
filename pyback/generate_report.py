import streamlit as st
import pandas as pd
import numpy as np

# 페이지 타이틀 설정
st.title("My Simple Dashboard")

# 사이드바 설정
st.sidebar.header("Dashboard Options")
num_points = st.sidebar.slider(
    "Number of points to plot:", 
    min_value=10, 
    max_value=100, 
    value=50
)

# 메인 페이지
st.header("Main Content Area")
st.write(f"Plotting **{num_points}** random data points.")

# 슬라이더 값에 따라 랜덤 데이터 생성
chart_data = pd.DataFrame(
    np.random.randn(num_points, 2),
    columns=['A', 'B']
)

# 라인 차트 표시
st.subheader("Dynamic Line Chart")
st.line_chart(chart_data)
