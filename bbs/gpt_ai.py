"""
AI 관련 서비스
"""
from openai import OpenAI

# from openai import OpenAI
from core import util

from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 환경 변수 사용
api_key = os.getenv("API_KEY")
gpt_model = os.getenv("GPT_MODEL")

# ChatGpt 연동
open_ai_key_main = api_key
model_engine = gpt_model

system_role = "너는 VAN 시스템에 대해서 잘 설명해줘야 해"

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
        model=model_engine_3,
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


if __name__ == '__main__':
    pass
