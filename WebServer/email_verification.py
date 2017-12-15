# -*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText

Host = "smtp.daum.net"
Port = 465


msg = MIMEText("안녕하세요? 온풀 서비스를 이용하기 위해서는 이메일 인증을 하셔야합니다.\n\n아래의 링크를 통해 인증을 완료하세요.\n\n\n%s"%
               ("http://onpul.return0927.xyz/email_verification?key=0230V9MU23490CRM390IM3049V2M304VTC4I23M40T234"))
msg['From'] = "bc1916@hanmail.net"
msg['To'] = "bc1916@hanmail.net"
#msg['To'] = "bjleh0927@gmail.com"
msg['Subject'] = "[온풀] 이메일 인증 / %s님의 이메일 인증코드입니다."%msg['To']


smtp = smtplib.SMTP_SSL(Host, Port)
smtp.login("bc1916", "leh81090306")
print(msg['From'], msg['To'])
result = smtp.sendmail(msg['From'], msg['To'], msg.as_string())
print(result)
smtp.quit()