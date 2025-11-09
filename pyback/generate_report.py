from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # return "Hello, Dashboard!" (이전 코드)
    return render_template('index.html') # 수정된 코드

if __name__ == '__main__':
    app.run(debug=True)