import base64
import hashlib
import json
import logging
import os
import random
import re
import shutil
import smtplib
import httpx
from datetime import datetime, timedelta, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import sleep
from typing import Any, List, Optional, Union
from urllib.parse import urlencode

from cachetools import LFUCache, TTLCache
from dotenv import load_dotenv
from fastapi import Request, UploadFile
from markupsafe import Markup, escape
from PIL import Image, ImageOps, UnidentifiedImageError
from passlib.context import CryptContext
from sqlalchemy import Index, asc, case, desc, func, select, delete, between, exists, cast, String, DateTime
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import URL
from user_agents import parse

from core.database import DBConnect, MySQLCharsetMixin
from core.models import (
    Auth, BoardNew, Config, Login, Member, Memo, Menu, NewWin, Poll, Popular,
    UniqId, Visit, VisitSum, WriteBaseModel
)
from lib.captcha.recaptch_v2 import ReCaptchaV2
from lib.captcha.recaptch_inv import ReCaptchaInvisible

import logging
from logging.handlers import TimedRotatingFileHandler

# 프로젝트 루트 경로에 log 폴더 경로 설정
log_directory = os.path.join(os.getcwd(), 'log')
log_file_name = 'gptforum.log'  # 변경: 고정된 파일 이름 지정
log_file_path = os.path.join(log_directory, log_file_name)

# log 폴더가 존재하지 않으면 생성
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 로거 설정 함수
def setup_logger():
    logger = logging.getLogger('GPTForumLogger')
    logger.setLevel(logging.INFO)

    # TimedRotatingFileHandler 설정
    handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    # 파일 이름에 날짜가 자동으로 포함되도록 suffix 설정은 제거하거나 조정
    handler.setFormatter(logging.Formatter('%(levelname)-6s:%(asctime)s:%(funcName)-24s:%(lineno)-5d - %(message)s'))
    logger.addHandler(handler)

    return logger

# 로거 설정
log = setup_logger()

load_dotenv()

# 전역변수 선언(global variables)
ENV_PATH = ".env"
CAPTCHA_PATH = "lib/captcha/templates"
EDITOR_PATH = "lib/editor/templates"


def hash_password(password: str):
    '''
    비밀번호를 해시화하여 반환하는 함수
    '''
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)  


def verify_password(plain_password, hashed_passwd):
    '''
    입력한 비밀번호와 해시화된 비밀번호를 비교하여 일치 여부를 반환하는 함수
    '''
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_passwd)  

# 동적 모델 캐싱: 모델이 이미 생성되었는지 확인하고, 생성되지 않았을 경우에만 새로 생성하는 방법입니다. 
# 이를 위해 간단한 전역 딕셔너리를 사용하여 이미 생성된 모델을 추적할 수 있습니다.
_created_models = {}

# 동적 게시판 모델 생성
def dynamic_create_write_table(
        table_name: str,
        create_table: bool = False,
    ) -> WriteBaseModel:
    '''
    WriteBaseModel 로 부터 게시판 테이블 구조를 복사하여 동적 모델로 생성하는 함수
    인수의 table_name 에서는 table_prefix + 'write_' 를 제외한 테이블 이름만 입력받는다.
    Create Dynamic Write Table Model from WriteBaseModel
    '''
    # log.info(
    #     f"[] 동적 테이블 클래스 생성 : 테이블 [{table_name}]"
    # )

    # 이미 생성된 모델 반환
    if table_name in _created_models:
        return _created_models[table_name]
    
    if isinstance(table_name, int):
        table_name = str(table_name)
    
    class_name = "Write" + table_name.capitalize()
    db_connect = DBConnect()

    DynamicModel = type(
        class_name, 
        (WriteBaseModel,), 
        {   
            "__tablename__": db_connect.table_prefix + 'write_' + table_name,
            "__table_args__": (
                Index(f'idx_wr_num_reply_{table_name}', 'wr_num', 'wr_reply'),
                Index(f'idex_wr_is_comment_{table_name}', 'wr_is_comment'),
                {
                    "extend_existing": True,
                    **MySQLCharsetMixin().__table_args__
                },
            ),
        }
    )

    # 게시판 추가시 한번만 테이블 생성
    if (create_table):
        DynamicModel.__table__.create(bind=db_connect.engine, checkfirst=True)

    # 생성된 모델 캐싱
    _created_models[table_name] = DynamicModel

    print(DynamicModel)

    return DynamicModel

def get_client_ip(request: Request) -> str:
    '''
    클라이언트의 IP 주소를 반환하는 함수 (PHP의 $_SERVER['REMOTE_ADDR'])
    '''
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # X-Forwarded-For can be a comma-separated list of IPs.
        # The client's requested IP will be the first one.
        return x_forwarded_for.split(",")[0]
    else:
        return request.client.host


async def get_host_public_ip():
    """
    호스트의 공인 IP 주소를 반환하는 함수
    """
    async with httpx.AsyncClient() as client:
        response = await client.get('https://httpbin.org/ip')
        return response.json()['origin']


def make_directory(directory: str):
    """이미지 경로 체크 및 생성

    Args:
        directory (str): 이미지 경로
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

# 파이썬의 내장함수인 list 와 이름이 충돌하지 않도록 변수명을 lst 로 변경함
def get_from_list(lst, index, default=0):
    if lst is None:
        return default
    try:
        return 1 if index in lst else default
    except (TypeError, IndexError):
        return default

def extract_browser(user_agent):
    # 사용자 에이전트 문자열에서 브라우저 정보 추출
    # 여기에 필요한 정규 표현식 또는 분석 로직을 추가
    # 예를 들어, 단순히 "Mozilla/5.0" 문자열을 추출하는 예제
    browser_match = re.search(r"Mozilla/5.0", user_agent)
    if browser_match:
        return "Mozilla/5.0"
    else:
        return "Unknown"


def select_query(request: Request, table_model, search_params: dict, 
        same_search_fields: Optional[List[str]] = "", # 값이 완전히 같아야지만 필터링 '검색어'
        prefix_search_fields: Optional[List[str]] = "", # 뒤에 %를 붙여서 필터링 '검색어%'
        default_sod: str = "asc",
        # default_sst: Optional[List[str]] = [],
        default_sst: str = "",
    ):
    config = request.state.config
    
    records_per_page = config.cf_page_rows

    db = DBConnect().sessionLocal()
    query = select()
    
    # # sod가 제공되면, 해당 열을 기준으로 정렬을 추가합니다.
    # if search_params['sst'] is not None and search_params['sst'] != "":
    #     # if search_params['sod'] == "desc":
    #     #     query = query.order_by(desc(getattr(table_model, search_params['sst'])))
    #     # else:
    #     #     query = query.order_by(asc(getattr(table_model, search_params['sst'])))
    #     if search_params.get('sod', default_sod) == "desc":  # 수정된 부분
    #         query = query.order_by(desc(getattr(table_model, search_params['sst'])))
    #     else:
    #         query = query.order_by(asc(getattr(table_model, search_params['sst'])))

    # 'sst' 매개변수가 제공되지 않거나 빈 문자열인 경우, default_sst를 사용합니다.
    sst = search_params.get('sst', default_sst) or default_sst
    # sod가 제공되면, 해당 열을 기준으로 정렬을 추가합니다.
    sod = search_params.get('sod', default_sod) or default_sod

    if sst:
        # sst 가 배열인 경우, 여러 열을 기준으로 정렬을 추가합니다.
        if isinstance(sst, list):
            for sort_attribute in sst:
                sort_column = getattr(table_model, sort_attribute)
                if sod == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        else:
            if sod == "desc":
                query = query.order_by(desc(getattr(table_model, sst)))
            else:
                query = query.order_by(asc(getattr(table_model, sst)))
        
            
    # sfl과 stx가 제공되면, 해당 열과 값으로 추가 필터링을 합니다.
    if search_params['sfl'] is not None and search_params['stx'] is not None:
        if hasattr(table_model, search_params['sfl']):  # sfl이 Table에 존재하는지 확인
            # if search_params['sfl'] in ["mb_level"]:
            if search_params['sfl'] in same_search_fields:
                query = query.where(getattr(table_model, search_params['sfl']) == search_params['stx'])
            elif search_params['sfl'] in prefix_search_fields:
                query = query.where(getattr(table_model, search_params['sfl']).like(f"{search_params['stx']}%"))
            else:
                query = query.where(cast(getattr(table_model, search_params['sfl']), String).like(f"%{search_params['stx']}%"))

    # 페이지 번호에 따른 offset 계산
    offset = (search_params['current_page'] - 1) * records_per_page
    # 최종 쿼리 결과를 가져옵니다.
    rows = db.scalars(query.add_columns(table_model).offset(offset).limit(records_per_page)).all()
    # 전체 레코드 개수 계산
    total_count = db.scalar(query.add_columns(func.count()).select_from(table_model).order_by(None))
    return {
        "rows": rows,
        "total_count": total_count,
    }

def nl2br(value) -> str:
    """ \n 을 <br> 태그로 변환
    """
    return escape(value).replace('\n', Markup('<br>\n'))

def get_unique_id(request) -> Optional[str]:
    """고유키 생성 함수
    그누보드 5의 get_uniqid

    년월일시분초00 ~ 년월일시분초99
    년(4) 월(2) 일(2) 시(2) 분(2) 초(2) 100만분의 1초(2)
    Args:
        request (Request): FastAPI Request 객체
    Returns:
        Optional[str]: 고유 아이디, DB 오류시 None
    """

    ip: str = get_client_ip(request)

    while True:
        current = datetime.now()
        ten_milli_sec = str(current.microsecond)[:2].zfill(2)
        key = f"{current.strftime('%Y%m%d%H%M%S')}{ten_milli_sec}"

        with DBConnect().sessionLocal() as session:
            try:
                session.add(UniqId(uq_id=key, uq_ip=ip))
                session.commit()
                return key

            except IntegrityError:
                # key 중복 에러가 발생하면 다시 시도
                session.rollback()
                sleep(random.uniform(0.01, 0.02))
            except Exception as e:
                logging.log(logging.CRITICAL, 'unique table insert error', exc_info=e)
                return None

def upload_file(upload_object, filename, path, chunck_size: int = None):
    """폼 파일 업로드
    Args:
        upload_object : form 업로드할 파일객체
        filename (str): 확장자 포함 저장할 파일명 (with ext)
        path (str): 저장할 경로
        chunck_size (int, optional): 파일 저장 단위. 기본값 1MB 로 지정
    Returns:
        str: 저장된 파일명
    """
    # 파일 저장 경로 생성
    os.makedirs(path, exist_ok=True)

    # 파일 저장 경로
    save_path = os.path.join(path, filename)
    # 파일 저장
    if chunck_size is None:
        chunck_size = 1024 * 1024
        with open(f"{save_path}", "wb") as buffer:
            shutil.copyfileobj(upload_object.file, buffer, chunck_size)
    else:
        with open(f"{save_path}", "wb") as buffer:
            shutil.copyfileobj(upload_object.file, buffer)


def get_filetime_str(file_path) -> Union[int, str]:
    """파일의 변경시간
    Args:
        file_path (str): 파일 이름포함 경로
    Returns:
        Union[int, str]: 파일 변경시간, 파일없을시 빈문자열
    """
    try:
        file_time = os.path.getmtime(file_path)
        return int(file_time)
    except FileNotFoundError:
        return ''


class StringEncrypt:
    def __init__(self, salt=''):
        if not salt:
            # You might want to implement your own salt generation logic here
            self.salt = "your_default_salt"
        else:
            self.salt = salt
        
        self.length = len(self.salt)

    def encrypt(self, str_):
        length = len(str_)
        result = ''

        for i in range(length):
            char = str_[i]
            keychar = self.salt[i % self.length]
            char = chr(ord(char) + ord(keychar))
            result += char

        result = base64.b64encode(result.encode()).decode()
        result = result.translate(str.maketrans('+/=', '._-'))

        return result

    def decrypt(self, str_):
        result = ''
        str_ = str_.translate(str.maketrans('._-', '+/='))
        str_ = base64.b64decode(str_).decode()

        length = len(str_)

        for i in range(length):
            char = str_[i]
            keychar = self.salt[i % self.length]
            char = chr(ord(char) - ord(keychar))
            result += char

        return result

# 사용 예
# enc = StringEncrypt()
# encrypted_text = enc.encrypt("hello")
# print(encrypted_text)

# decrypted_text = enc.decrypt(encrypted_text)
# print(decrypted_text)


def is_possible_ip(request: Request, ip: str) -> bool:
    """IP가 접근허용된 IP인지 확인

    Args:
        request (Request): FastAPI Request 객체
        ip (str): IP

    Returns:
        bool: 허용된 IP이면 True, 아니면 False
    """
    cf_possible_ip = request.state.config.cf_possible_ip
    return check_ip_list(request, ip, cf_possible_ip, allow=True)


def is_intercept_ip(request: Request, ip: str) -> bool:
    """IP가 접근차단된 IP인지 확인

    Args:
        request (Request): FastAPI Request 객체
        ip (str): IP

    Returns:
        bool: 차단된 IP이면 True, 아니면 False
    """
    cf_intercept_ip = request.state.config.cf_intercept_ip
    return check_ip_list(request, ip, cf_intercept_ip, allow=False)


def check_ip_list(request: Request, current_ip: str, ip_list: str, allow: bool) -> bool:
    """IP가 특정 목록에 속하는지 확인하는 함수

    Args:
        request (Request): FastAPI Request 객체
        ip (str): IP
        ip_list (str): IP 목록 문자열
        allow (bool): True인 경우 허용 목록, False인 경우 차단 목록

    Returns:
        bool: 목록에 속하면 True, 아니면 False
    """
    if request.state.is_super_admin:
        return allow

    ip_list = ip_list.strip()
    if not ip_list:
        return allow

    ip_patterns = ip_list.split("\n")
    for pattern in ip_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        pattern = pattern.replace(".", r"\.")
        pattern = pattern.replace("+", r"[0-9\.]+")
        if re.match(f"^{pattern}$", current_ip):
            return True

    return False


def filter_words(request: Request, contents: str) -> str:
    """글 내용에 필터링된 단어가 있는지 확인하는 함수

    Args:
        request (Request): FastAPI Request 객체
        contents (str): 글 내용

    Returns:
        str: 필터링된 단어가 있으면 해당 단어, 없으면 빈 문자열
    """
    cf_filter = request.state.config.cf_filter
    words = cf_filter.split(",")
    for word in words:
        word = word.strip()
        if not word:
            continue
        if word in contents:
            return word

    return ''

def remove_query_params(request: Request, keys: Union[str, list]) -> dict:
    """쿼리 파라미터에서 특정 키를 제거합니다.

    Args:
        request (Request): FastAPI Request 객체
        keys (Union[str, list]): 제거할 키

    Returns:
        dict: 쿼리 파라미터
    """
    query_params_dict = dict(request.query_params)

    if isinstance(keys, str):
        keys = [keys]

    for key in keys:
        query_params_dict.pop(key, None)

    return query_params_dict


def set_url_query_params(url: Union[str, URL], query_params: Any) -> str:
    """쿼리 파라미터가 포함된 URL을 반환합니다.

    Args:
        url (URL): URL 객체
        query_params (Any): 쿼리 파라미터

    Returns:
        URL: 쿼리 파라미터가 포함된 URL
    """
    if isinstance(url, str):
        url = URL(url)

    return url.replace_query_params(**query_params).__str__()


def is_integer_format(s):
    if not s:
        return False
    if s[0] == "-":
        s = s[1:]
    return s.isdigit()