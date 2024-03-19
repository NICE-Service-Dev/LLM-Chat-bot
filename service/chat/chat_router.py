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
