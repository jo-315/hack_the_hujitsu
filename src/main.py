from flask import render_template, request
from src import app

# 最初の検索画面
@app.route('/', methods=['GET'])
def index():

    return render_template("index.html")