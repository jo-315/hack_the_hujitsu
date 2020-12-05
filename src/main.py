from flask import render_template, request
from src import app

# 最初の検索画面
@app.route('/', methods=['GET'])
def index():

    return render_template("index.html", m='sss')


# javascriptからのAPIを受け取って歩数を返す
@app.route('/fetch', methods=['GET'])
def fetch():
    # TODO: 歩数をAPIで取得（google fit api）
    steps = 10

    return {'steps': steps}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)