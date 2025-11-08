import streamlit as st

# 페이지 타이틀 설정
st.title("My Simple Dashboard")

# 사이드바 설정
st.sidebar.header("Dashboard Options")
st.sidebar.write("Options will go here.")

# 메인 페이지
st.header("Main Content Area")
st.write("Welcome to my first Streamlit app!")
