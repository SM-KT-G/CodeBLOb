# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.title('간단한 파이썬 대시보드 📊')

# 1. 사이드바에 슬라이더 위젯 추가
st.sidebar.header('옵션 선택')
num_points = st.sidebar.slider('표시할 데이터 개수:', 10, 100, 50) # (라벨, 최소, 최대, 기본값)

st.write(f'총 **{num_points}개**의 데이터를 표시합니다.')

# 2. 슬라이더 값에 따라 동적으로 데이터 생성
@st.cache_data
def get_data(num_points):
    data = np.random.randn(num_points, 2)
    df = pd.DataFrame(data, columns=['A', 'B'])
    return df

df = get_data(num_points) # 슬라이더 값을 인자로 전달

st.header('동적 라인 차트')
st.line_chart(df)

# 3. 체크박스로 데이터 숨기기/보이기
if st.checkbox('데이터 원본 보기'):
    st.dataframe(df)
