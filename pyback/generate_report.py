# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.title('간단한 파이썬 대시보드')
st.write('Streamlit을 이용한 첫 번째 대시보드입니다.')

# 샘플 데이터 생성
@st.cache_data  # 데이터 캐싱
def get_data():
    data = np.random.randn(50, 2)
    df = pd.DataFrame(data, columns=['A', 'B'])
    return df

df = get_data()

st.header('간단한 라인 차트')
st.line_chart(df)

st.header('데이터 원본')
st.dataframe(df)
