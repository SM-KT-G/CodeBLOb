from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # 동적 데이터 생성
    dashboard_data = {
        'title': 'My Dynamic Dashboard',
        'metrics': [
            {'name': 'Active Users', 'value': 120},
            {'name': 'Sales', 'value': '15,000 $'}
        ]
    }
    # 데이터를 템플릿으로 전달
    return render_template('index.html', data=dashboard_data)

if __name__ == '__main__':
    app.run(debug=True)