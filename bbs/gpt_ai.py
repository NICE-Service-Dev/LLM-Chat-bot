"""
AI 관련 서비스
"""
from openai import OpenAI
from fastapi import FastAPI, WebSocket, Request

# from openai import OpenAI
from core import util

from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# FastAPI 로
app = FastAPI()

# 환경 변수 사용
api_key = os.getenv("API_KEY")
gpt_model = os.getenv("GPT_MODEL")

# ChatGpt 연동
open_ai_key_main = api_key
model_engine = gpt_model

system_role = "문단나누기나 들여쓰기 잘해서 답변줘야해"

# openai.api_key = open_ai_key_main
client = OpenAI(
    api_key=open_ai_key_main
)

"""
Open AI : GPT 서비스
"""
"""
GPT 프롬프트 제출 및 내용 생성
"""
def gpt_create(prompt):
    # print(f"open api key = [{openai.api_key}]")
    print("============================================================")
    print(f"GPT4 명령 프롬프트 : [{prompt}]")

    resp = client.chat.completions.create(
        model=model_engine,
        messages=[
            {"role": "user", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=1
    )

    result_msg = resp.choices[0].message.content

    print("============================================================")
    print(f"[GPT 생성 결과]")
    print("============================================================")
    print(f"{result_msg}")
    print("============================================================")

    return result_msg

"""
GPT 프롬프트 생성
"""
def gpt_prompt_create(subject):
    return f"""{subject}를 주제로 사용자에게 설명해줘
"""

def generate_completion(client: OpenAI, text: str) -> str:
    completion = client.generate(prompt=text, model=gpt_model)
    return completion


def print_received_data(ip: str, port: int, data: str, completion: str):
    # 수신된 데이터와 생성된 응답을 콘솔에 출력하는 함수입니다.
    print(f"Received text: ({ip}:{port}): {data} -> {completion}")

async def send_response(websocket: WebSocket, original_text: str, completion: str):
    # 웹소켓을 통해 클라이언트에게 응답 메시지를 전송하는 함수입니다.
    response = f"Message text was: {original_text} -> {completion}"
    await websocket.send_text(response)

if __name__ == '__main__':
    pass
