function sendMessage() {
    const input = document.getElementById("userInput");
    const chatOutput = document.getElementById("chatOutput");
    const userText = input.value.trim();

    if (userText !== "") {
        // 사용자 입력을 채팅에 추가
        chatOutput.innerHTML += `<div>User: ${userText}</div>`;

        // 답변 로직 (여기서는 단순 예제)
        const botReply = "Let me think...";
        chatOutput.innerHTML += `<div>Bot: ${botReply}</div>`;

        // 입력 필드 초기화
        input.value = "";

        // 스크롤을 최신 메시지로 이동
        chatOutput.scrollTop = chatOutput.scrollHeight;
    }
}

jQuery(document).ready(function() {

    $(".chat-list a").click(function() {
        $(".chatbox").addClass('showbox');
        return false;
    });

    $(".chat-icon").click(function() {
        $(".chatbox").removeClass('showbox');
    });


});
