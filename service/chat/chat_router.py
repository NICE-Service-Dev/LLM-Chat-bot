"""
나이스 CHAT 라우터
"""
from fastapi import APIRouter, WebSocket, Depends, Request,FastAPI
from fastapi.templating import Jinja2Templates

from bbs.gpt_ai import generate_completion, print_received_data, send_response, gpt_create

"""CHAT 서비스 import"""
import service.chat.chat_svc as svc
from core import util

router = APIRouter()

templates = Jinja2Templates(directory="templates")

"""
나이스 CHAT 메시지 Send
"""
@router.websocket("/send")
async def post_create_ai(websocket: WebSocket):
    await websocket.accept()
    print("[/chat/send] WebSocket Start")

    while True:
        data = await websocket.receive_json()
        msg,subject = data['msg'], data['subject']

        print(f"WebSocket server recv : msg [{msg}], subject [{subject}]")

        # chat gpt 로 보내기
        await websocket.send_text(f"{gpt_create(msg)}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # 웹소켓 연결을 수락합니다.
    client_ip, client_port = websocket.client  # 클라이언트의 IP와 포트를 가져옵니다.
    print(f"Connection from: {client_ip}:{client_port}")  # 연결된 클라이언트 정보를 콘솔에 출력합니다.
    while True:
        data = await websocket.receive_json()  # 웹소켓을 통해 텍스트 데이터를 수신합니다.
        msg, subject = data['msg'], data['subject']
        print(f"WebSocket server recv : msg [{msg}], subject [{subject}]")
        completion = await generate_completion(msg)  # 수신된 텍스트에 대한 응답을 생성합니다.
        print_received_data(client_ip, client_port, data, completion)  # 수신 및 응답 데이터를 출력합니다.
        await send_response(websocket, data, completion)  # 웹소켓을 통해 응답을 클라이언트에게 전송합니다.