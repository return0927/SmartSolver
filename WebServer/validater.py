import re
from dateutil.parser import parse
from datetime import datetime, timedelta

re_email = re.compile('[^@]+@[^@]+\.[^@]+')

def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


def birthday(string):
    if not is_date(string): return [True, "올바른 형식이 아닙니다."]

    try:
        b_d = datetime.strptime(string, '%Y-%m-%d')
        if b_d > (datetime.now() - timedelta(years=15)):
            return [True, "만 15세 미만은 가입하실 수 없습니다."]
        else:
            return [False, ""]
    except Exception as ex:
        return [True, "올바른 형식이 아닙니다."]

def email(string):
    if not re_email.match(string):
        return [True, "올바른 형식이 아닙니다."]
    else:
        return [False, ""]