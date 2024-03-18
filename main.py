import datetime
import os

from fastapi import FastAPI, Path, Request, Response,WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import TypeAdapter
# from sqlalchemy import select, insert, inspect
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

from core.middleware import should_run_middleware, regist_core_middleware
from core.exception import (
    AlertException,
    regist_core_exception_handler,
    template_response
)

APP_IS_DEBUG = TypeAdapter(bool).validate_python(os.getenv("APP_IS_DEBUG", False))
#
# # APP_IS_DEBUG 값이 True일 경우, 디버그 모드가 활성화됩니다.
# app = FastAPI(debug=APP_IS_DEBUG)

"""
FastAPI 기본 설정
"""
app = FastAPI()

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# 각 경로에 있는 파일들을 정적 파일로 등록합니다.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

# 미들웨어 등록
regist_core_middleware(app)

# 예외처리 핸들러 등록
regist_core_exception_handler(app)

"""
라우터 등록
"""
from service.chat.chat_router import router as chat_router

app.include_router(chat_router, prefix="/chat", tags=["chat"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # `request`는 템플릿에 컨텍스트를 전달하기 위해 필요합니다.
    return templates.TemplateResponse("chat/chat_index.html", {"request": request})
