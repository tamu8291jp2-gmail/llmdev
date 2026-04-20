import pytest

from original.app import app
from original.graph import memory

USER_MESSAGE_1 = "こんにちは！"


@pytest.fixture
def client():
    """
    Flaskテストクライアントを作成。
    """
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session.clear()  # セッションをクリアして初期化

    yield client


def test_index_get_request(client):
    """
    GETリクエストで初期画面が正しく表示され、セッションとメモリが初期化されるかテスト。
    """
    # テスト用のセッションをあらかじめ設定しておく
    with client.session_transaction() as session:
        session["thread_id"] = "test_thread"

    response = client.get("/")

    assert response.status_code == 200, (
        "GETリクエストに対してステータスコード200を返すべきです。"
    )
    assert b'id="chat-box"' in response.data, (
        "HTMLにチャットボックス要素が含まれている必要があります。"
    )

    # セッションとメモリがクリアされているか確認
    with client.session_transaction() as session:
        assert "thread_id" not in session, (
            "GETリクエストでセッションのthread_idが削除されるべきです。"
        )
    assert memory.storage == {}, "GETリクエストでメモリが空になるべきです。"


def test_chat_endpoint(client):
    """
    POSTリクエスト（非同期通信）でボットの応答がJSONで正しく返されるかをテスト。
    """
    # 非同期通信（Fetch API）に合わせて、json形式でリクエストを送信
    response = client.post("/chat", json={"user_message": USER_MESSAGE_1})

    assert response.status_code == 200, (
        "POSTリクエストに対してステータスコード200を返すべきです。"
    )

    # 返ってきたJSONレスポンスを取得して確認
    data = response.get_json()
    assert "bot_message" in data, (
        "レスポンスのJSONに 'bot_message' が含まれている必要があります。"
    )
    assert data["bot_message"] != "", "ボットからの応答が空ではない必要があります。"

    # セッションにthread_idが生成されているか確認
    with client.session_transaction() as session:
        assert "thread_id" in session, (
            "POSTリクエスト後にはセッションにthread_idが設定されているべきです。"
        )


def test_clear_endpoint(client):
    """
    /clearエンドポイントがセッションとメモリを正しくリセットするかをテスト。
    """
    # 事前にチャットを1回送信してセッションとメモリを作成
    client.post("/chat", json={"user_message": USER_MESSAGE_1})

    with client.session_transaction() as session:
        thread_id = session.get("thread_id")
        assert thread_id is not None, (
            "POSTリクエスト後にはセッションにthread_idが設定されているべきです。"
        )

    # clearエンドポイントを実行
    response = client.post("/clear")

    # トップページへ redirect(url_for('index')) しているため、ステータスコードは302（リダイレクト）になる
    assert response.status_code == 302, (
        "/clearエンドポイントはリダイレクト(302)を返すべきです。"
    )

    # セッションとメモリがクリアされているか確認
    with client.session_transaction() as session:
        assert "thread_id" not in session, (
            "/clearエンドポイント後にはセッションからthread_idが削除されているべきです。"
        )

    cleared_messages = memory.get({"configurable": {"thread_id": thread_id}})
    assert cleared_messages is None, (
        "メモリは/clearエンドポイント後にクリアされるべきです。"
    )
