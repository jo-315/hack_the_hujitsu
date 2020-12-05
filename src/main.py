from flask import render_template, request
from src import app

# 最初の検索画面
@app.route('/', methods=['GET'])
def index():
    msg = "歩数を記録"
    point={"ロンドン":"https://www.google.com/maps/embed?pb=!4v1607025863243!6m8!1m7!1sierMTh4ePdwoKu6_7IiCvA!2m2!1d51.50897647482117!2d-0.08739389902462565!3f180!4f0!5f0.7820865974627469","ラスベガス":"https://www.google.com/maps/embed?pb=!4v1607026447718!6m8!1m7!1s2OlsjeKFZu4GQN0EOi4lHA!2m2!1d36.11234006692544!2d-115.1749467008171!3f90!4f0!5f0.7820865974627469"  }
    return render_template("index.html", msg = msg,point =  point)

#  javascriptからのAPIを受け取って歩数を返す
@app.route('/fetch', methods=['GET'])
def fetch():
    # TODO: 歩数をAPIで取得（google fit api）
    steps = 10

    return {'steps': steps}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
