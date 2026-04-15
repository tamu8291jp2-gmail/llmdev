# 課題：ユーザー認証を行うクラスのテストコードを作成しよう

import pytest
from authenticator import Authenticator


@pytest.fixture
def authenticator():
    auth = Authenticator()
    yield auth


# ユーザーの登録関数 register のテスト
# ユーザーが正しく登録されるか
@pytest.mark.parametrize(
    "username, password",
    [
        ("JohnDoe123", "password123"),  # 一般的な例
        ("user1", "pass1"),  # 最小文字数(5文字)
        ("UserName1234567", "longpw"),  # 最大文字数(15文字)
        ("Alice", "alice_pass"),  # 英字のみ
    ],
)
def test_register_success(authenticator, username, password):
    authenticator.register(username, password)
    assert authenticator.users[username] == password


# ユーザーの登録関数 register のテスト
# すでに存在するユーザー名で登録を試みた場合に、エラーメッセージが出力されるか
@pytest.mark.parametrize(
    "username, password",
    [
        ("JohnDoe123", "password123"),  # 一般的な例
        ("user1", "pass1"),  # 最小文字数(5文字)
        ("UserName1234567", "longpw"),  # 最大文字数(15文字)
        ("Alice", "alice_pass"),  # 英字のみ
    ],
)
def test_register_duplicate(authenticator, username, password):
    authenticator.register(username, password)
    with pytest.raises(ValueError, match="エラー: ユーザーは既に存在します。"):
        authenticator.register(username, password)


# ログイン関数 login のテスト
# 正しいユーザー名とパスワードでログインできるか
@pytest.mark.parametrize(
    "username, password",
    [
        ("JohnDoe123", "password123"),  # 一般的な例
        ("user1", "pass1"),  # 最小文字数(5文字)
        ("UserName1234567", "longpw"),  # 最大文字数(15文字)
        ("Alice", "alice_pass"),  # 英字のみ
    ],
)
def test_login_valid_user(authenticator, username, password):
    authenticator.register(username, password)
    result = authenticator.login(username, password)
    assert result == "ログイン成功"


# ログイン関数 login のテスト
# 誤ったパスワードでエラーが出るか
@pytest.mark.parametrize(
    "username, correct_password, wrong_password",
    [
        ("JohnDoe123", "password123", "wrongpass"),  # 一般的な例
        ("user1", "pass1", "pass2"),  # 最小文字数(5文字)
        ("UserName1234567", "longpw", "longwrongpw"),  # 最大文字数(15文字)
        ("Alice", "alice_pass", "alice_wrongpass"),  # 英字のみ
    ],
)
def test_login_wrong_password(
    authenticator, username, correct_password, wrong_password
):
    authenticator.register(username, correct_password)
    with pytest.raises(
        ValueError, match="エラー: ユーザー名またはパスワードが正しくありません。"
    ):
        authenticator.login(username, wrong_password)
