# 標準ライブラリ
import os
import sys
import uuid

# 外部ライブラリ
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# VS Codeのデバッグ実行で自作モジュールのエラーを出さない対策
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 自作モジュールのインポート
from original.graph import MODEL_NAME, get_bot_response, get_messages_list, memory

# Flaskアプリケーションのセットアップ
app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッション用の秘密鍵


# ニュースを取得する関数
def get_latest_news():
    url = "https://www.artificialintelligence-news.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 記事の主要部分を抽出し、長すぎる場合のために3万文字で制限をかける
    main_content = soup.find("main") or soup.find("article") or soup.body
    html_text = str(main_content)[:30000]

    llm = ChatOpenAI(model_name=MODEL_NAME)
    messages = [
        SystemMessage(
            content="あなたは可愛い猫のキャラクターだにゃ。挨拶や説明など、すべての文章の語尾に必ず「にゃ」や「にゃん」をつけて話すにゃ。マジメな言葉遣いは禁止だにゃ。"
        ),
        HumanMessage(
            content=f"以下のHTMLから最新ニュース5件のタイトルとリンクを抽出し、タイトルを日本語に翻訳してリスト形式で出力してにゃ。\n\nHTML:{html_text}"
        ),
    ]
    result = llm.invoke(messages)
    return result.content


@app.route("/get_news", methods=["GET"])
def get_news_endpoint():
    # ニュースを取得して返す
    news_text = get_latest_news()
    return jsonify({"text": news_text.replace("\n", "<br>")})


@app.route("/", methods=["GET"])
def index():
    # メモリをクリア
    memory.storage.clear()
    # セッションからthread_idを削除
    if "thread_id" in session:
        session.pop("thread_id", None)
    # 画面の枠組みだけを表示
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    # セッションからthread_idを取得、なければ新しく生成してセッションに保存
    if "thread_id" not in session:
        session["thread_id"] = str(uuid.uuid4())  # ユーザー毎にユニークなIDを生成

    data = request.json
    user_message = data.get("user_message")

    # ボットのレスポンスを取得（メモリに保持）
    get_bot_response(user_message, memory, session["thread_id"])
    # メモリからメッセージの取得
    messages = get_messages_list(memory, session["thread_id"])
    # メモリから最新のボットのメッセージだけを取得して返す
    bot_message_text = messages[-1]["text"]  # リストの最後が最新の回答
    return jsonify({"bot_message": bot_message_text})


@app.route("/clear", methods=["POST"])
def clear():
    # セッションからthread_idを削除
    session.pop("thread_id", None)
    # メモリをクリア
    memory.storage.clear()
    # 履歴消去時はトップページにリダイレクト
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
