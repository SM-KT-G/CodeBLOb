import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# 샘플 데이터 생성
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Grapes"],
    "Amount": [4, 1, 2, 2],
})

# 플로틀리(Plotly) 그래프 생성
fig = px.bar(df, x="Fruit", y="Amount", title="Fruit Distribution")

# Dash 앱 초기화
app = dash.Dash(__name__)

# 대시보드 레이아웃 정의
app.layout = html.Div(children=[
    # H1 태그로 제목 추가
    html.H1(children='간단한 Dash 대시보드'),

    # 간단한 설명 추가
    html.Div(children='''
        Dash: 파이썬으로 웹 애플리케이션 만들기
    '''),

    # dcc.Graph 컴포넌트로 그래프 표시
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

# 서버 실행
if __name__ == '__main__':
    app.run_server(debug=True)
