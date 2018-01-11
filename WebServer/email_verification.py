# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

Host = "smtp.daum.net"
Port = 465

def send(code, email):
    try:
        _send(code)
        return [False, None]
    except Exception as ex:
        return [True, str(ex)]

def _send(code, email):
    msg = MIMEMultipart('alternative')

    txt = MIMEText("""
        <h2>온풀 서비스</h2>
        <p>안녕하세요? 수학을 쉽게, 온풀입니다.</p>
        <p>고객님의 원활한 서비스 이용을 위해 이메일의 소유권을 인증하셔야 합니다.</p>
        <br>
        <p>아래의 링크를 클릭하여 이메일 인증을 완료해주세요.</p>
        <a target="_blank" href="http://onpool.kr/verify?code={}" rel="noopener noreferrer">인증하기</a>
    """.format(code), 'html')

    msg.attach(txt)

    msg['From'] = "service@onpool.kr"
    msg['To'] = email
    msg['Subject'] = "[온풀] 이메일 인증 / %s님의 이메일 인증코드입니다."%msg['To']


    smtp = smtplib.SMTP_SSL(Host, Port)
    smtp.login("bc1916", "leh81090306")
    print(msg['From'], msg['To'])
    result = smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    print(result)
    smtp.quit()

