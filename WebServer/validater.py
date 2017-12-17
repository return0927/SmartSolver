# -*- coding:utf-8 -*-
import re
import smtplib
from email.mime.text import MIMEText
from dateutil.parser import parse
from datetime import datetime
from dateutil.relativedelta import relativedelta

re_email = re.compile('[^@]+@[^@]+\.[^@]+')

def is_date(string):
    try:
        datetime.strptime(string, '%Y-%m-%d')
        return True
    except Exception as ex:
        print(ex)
        return False


def birthday(string):
    if is_date(string) is False: return [True, "올바른 형식이 아닙니다."]

    try:
        b_d = datetime.strptime(string, '%Y-%m-%d')
        if b_d + relativedelta(years=15) > datetime.now():
            return [True, "만 15세 미만은 가입하실 수 없습니다."]
        else:
            return [False, ""]
    except Exception as ex:
        print(ex)
        return [True, "올바른 형식이 아닙니다."]


def email(string):
    if not re_email.match(string):
        return [True, "올바른 형식이 아닙니다."]
    else:
        return [False, ""]


def sendVerf(_email, string):
    try:
        Host = "smtp.daum.net"
        Port = 465

        msg = MIMEText("안녕하세요? 온풀 서비스를 이용하기 위해서는 이메일 인증을 하셔야합니다.\n\n아래의 링크를 통해 인증을 완료하세요.\n\n\n%s" %
                       ("http://onpul.return0927.xyz/email_verification?key=%s"%string))
        msg['From'] = "bc1916@hanmail.net"
        msg['To'] = _email
        msg['Subject'] = "[온풀] 이메일 인증 / %s님의 이메일 인증코드입니다." % msg['To']

        smtp = smtplib.SMTP_SSL(Host, Port)
        smtp.login("bc1916", "leh81090306")

        print(msg['From'], msg['To'])
        result = smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        print(result)
        smtp.quit()

        return [str(result) == "{}", result]
    except Exception as ex:
        print(" 이메일인증 메일전송 오류 (%s) %s"%(_email, str(ex)))
        return [False, str(ex)]
