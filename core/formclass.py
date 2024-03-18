from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from fastapi import Form

"""
FrontEnd 요청시 Request DTO
>> 예시만 남겨놓은 ( NICE CHAT )
>> Front Form 제출시 사용 
"""

@dataclass
class MemberForm:
    # mb_password: Optional[str] = Form(default="")
    mb_name: str = Form(None)
    mb_birth: Optional[str] = Form(default="")
    mb_nick: str = Form(None)
    # mb_nick_date: Optional[str] = Form(default=None)
    mb_level: Optional[int] = Form(default=0)
    mb_email: Optional[str] = Form(default="")
    mb_homepage: Optional[str] = Form(default="")
    mb_sex: Optional[str] = Form(default="")
    mb_recommend: Optional[str] = Form(default="")
    mb_hp: Optional[str] = Form(default="")
    mb_tel: Optional[str] = Form(default="")
    mb_certify: Optional[int] = Form(default=0)
    mb_adult: Optional[int] = Form(default=0)
    mb_addr_jibeon: Optional[str] = Form(default="")
    mb_zip1: Optional[str] = Form(default="")
    mb_zip2: Optional[str] = Form(default="")
    mb_addr1: Optional[str] = Form(default="")
    mb_addr2: Optional[str] = Form(default="")
    mb_addr3: Optional[str] = Form(default="")
    mb_mailling: Optional[int] = Form(default=0)
    mb_sms: Optional[int] = Form(default=0)
    mb_open: Optional[int] = Form(default=0)
    mb_signature: Optional[str] = Form(default="")
    mb_profile: Optional[str] = Form(default="")
    mb_memo: Optional[str] = Form(default="")
    # mb_intercept_date: Optional[str] = Form(default="")
    # mb_leave_date: Optional[str] = Form(default="")
    mb_1: Optional[str] = Form(default="")
    mb_2: Optional[str] = Form(default="")
    mb_3: Optional[str] = Form(default="")
    mb_4: Optional[str] = Form(default="")
    mb_5: Optional[str] = Form(default="")
    mb_6: Optional[str] = Form(default="")
    mb_7: Optional[str] = Form(default="")
    mb_8: Optional[str] = Form(default="")
    mb_9: Optional[str] = Form(default="")
    mb_10: Optional[str] = Form(default="")

