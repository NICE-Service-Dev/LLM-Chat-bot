"""
공통 util 관련
"""
from datetime import datetime




"""
파일 관련 util
"""
def save_text_file(text,file_path,file_name):
    """
    주어진 문자열을 텍스트 파일로 저장합니다.

    Args:
        text (str): 파일에 저장할 문자열.
        file_path (str): 생성될 파일 경로.
        file_name (str): 생성될 파일의 이름.
    """
    # 파일 자르기
    s_day = datetime.now()
    file_day = s_day.strftime('%Y%m%d')
    same_day_gb = s_day.strftime('%M%S')

    filename = file_day+"_"+file_name +"_" +same_day_gb
    file = f'data/txt/{file_path}/{filename}.txt'
    print(f"저장 파일 이름 : [{filename}]")

    # 파일을 쓰기 모드로 열기
    with open(file, 'w', encoding='utf-8') as file:
        file.write(text)  # 문자열을 파일에 쓰기