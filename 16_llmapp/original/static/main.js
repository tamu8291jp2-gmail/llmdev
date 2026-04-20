window.onload = function() {
    const chatBox = document.getElementById('chat-box');
    const textarea = document.getElementById('user-input');
    const submitButton = document.getElementById('submit-button');

    // 1. 初期表示時のニュース取得
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'bot-message';
    loadingDiv.innerHTML = "最新ニュースを取得中にゃ... 少し待っててにゃ！⏳";
    chatBox.appendChild(loadingDiv);

    // ローディングメッセージを表示した直後にも一番下へスクロール
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch('/get_news')
        .then(response => response.json())
        .then(data => {
            loadingDiv.innerHTML = "最新ニュースの取得が完了したにゃ！✨";
            // ニュース本文を追加
            const newsDiv = document.createElement('div');
            newsDiv.className = 'bot-message';
            newsDiv.innerHTML = data.text;
            chatBox.appendChild(newsDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            loadingDiv.innerHTML = "ニュースの取得に失敗したにゃ💦";
        });

    // 2. チャット送信の非同期処理
    function sendMessage() {
        const text = textarea.value.trim();
        if (text === "") return;

        // ユーザーのメッセージを画面に追加
        const userDiv = document.createElement('div');
        userDiv.className = 'user-message';
        // ユーザーの入力の改行(\n)をHTMLの改行(<br>)に変換して表示
        userDiv.innerHTML = text.replace(/\n/g, '<br>');
        chatBox.appendChild(userDiv);
        
        textarea.value = ""; // 入力欄を空にする
        chatBox.scrollTop = chatBox.scrollHeight;

        // ボットの「考え中...」メッセージを表示
        const botLoadingDiv = document.createElement('div');
        botLoadingDiv.className = 'bot-message';
        botLoadingDiv.innerHTML = "考え中にゃ...💭";
        chatBox.appendChild(botLoadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        // 裏側でFlaskの '/chat' に送信（非同期通信）
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_message: text })
        })
        .then(response => response.json())
        .then(data => {
            // サーバーから返ってきた回答で「考え中...」を上書き
            botLoadingDiv.innerHTML = data.bot_message;
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            botLoadingDiv.innerHTML = "エラーが発生したにゃ💦";
        });
    }

    // ボタンクリックで送信
    submitButton.addEventListener('click', sendMessage);

    // Ctrl+Enterで送信
    textarea.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
}