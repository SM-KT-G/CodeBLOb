import streamlit as st

# 페이지 타이틀 설정
st.title("My Simple Dashboard")

# 사이드바 설정
st.sidebar.header("Dashboard Options")
number = st.sidebar.slider("Choose a number:", min_value=0, max_value=100, value=50)

# 메인 페이지
st.header("Main Content Area")
st.write(f"You selected the number: **{number}**")
