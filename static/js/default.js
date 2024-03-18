/* TEST */
function testConJs() {
    console.log("default.js connect")
}

/* WebSocket */
// 웹소켓 송신
function wsSend(ws,data) {
    /* 웹소켓 연결 */
    ws.onopen = function () {
        console.log("[/post/create/ai] WebSocket connection established");
    };

    /* 웹소켓 송신 - 메시지 송신 */
    ws.send(JSON.stringify(data));
};

// 웹소켄 수신
function wsRecv(ws, fn) {
    ws.onmessage = fn
}


/* AJAX 통신 */

// Post 통신
function ajaxPost(url, data, success_fn) {
    $.ajax({
        type: 'post',           // 타입 (get, post, put 등등)
        url: url,           // 요청할 서버url
        dataType: 'json',       // 데이터 타입 (html, xml, json, text 등등) 'json' 원래
        data: JSON.stringify(data),
        async: false,
        success: success_fn,
        error: function (request, status, error) { // 결과 에러 콜백함수
            console.log("POST 서버 통신 실패 : ", error)
        }
    })
}

// GET 통신
function ajaxGet(url, data, success_fn) {
    $.ajax({
        type: 'get',           // 타입 (get, post, put 등등)
        url: url,           // 요청할 서버url
        dataType: 'json',       // 데이터 타입 (html, xml, json, text 등등)
        data: JSON.stringify(data),
        async: false,
        success: success_fn,
        error: function (request, status, error) { // 결과 에러 콜백함수
            console.log("GET 서버 통신 실패 : ", error)
        }
    })
}

/* Util */
// 시간:분 가져오기
function getHoursMinutes() {
    const now = new Date(); // 현재 날짜와 시간을 나타내는 Date 객체 생성

    let hours = now.getHours(); // 현재 시간(0-23)을 가져옴
    let minutes = now.getMinutes(); // 현재 분(0-59)을 가져옴

    // 시간과 분을 두 자리 숫자로 맞추기
    hours = hours.toString().padStart(2, '0');
    minutes = minutes.toString().padStart(2, '0');

    // "HH:MM" 형식으로 포맷된 문자열 반환
    return `${hours}:${minutes}`;
}