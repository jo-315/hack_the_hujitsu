# 富士通 Hack the Future(京FC)
テーマ：おうち町歩き

### 環境
flamework: Flask

## 環境構築
ルートディレクトリで`docker-compose build`

### localでの起動コマンド
`docker-compose up`  
※`-d`をつけるとバックグラウンドで実行

### ブラウザ表示
`localhost:5050`

## ファイル構造
- `src`内にファイルを配置（それ以外は設定ファイル）
- `.main.py`: バックエンドのファイル。ここに、歩行の処理やらなんやらを書きましょう
- `templates/ndex.html`: ブラウザに表示されるファイル。`jinja2`というpythonとhtmlの中間的なファイルです。

## git
1. ブランチ切る
2. ローカル（自分のPC）で作業する→コミット
3. リモートにpush
4. gitのHPにきてプルリクエストを作る

## dockerコマンド
- 実行
`docker-compose up`

- バックグラウンド
`docker-compose up`

- 停止
`docker-compose stop`

- コンテナ内に入る(flask)
`docker-compose exec flask bash`

- コンテナ内に入る(DB: postgres)
`docker-compose exec postgres bash`

- db初期化
`docker-compose down -v`

# Flask
デバッグ
app.logger.debug("デバッグメッセージ")
