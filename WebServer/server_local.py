import hashlib
import json
import validater
import string
import random
import threading
from urllib.parse import parse_qs
from datetime import datetime
# from OpenSSL import SSL

# import db
import general_settings
import email_verification
from flask import *

gSet = general_settings.Settings()
# DB = db.DB()

app = Flask(__name__)
app.config['SECRET_KEY'] = gSet.hostKey
encrypt = lambda x: hashlib.sha256(x.encode()).hexdigest().upper()

# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_certificate_file("ssl.crt")
# context.use_privatekey_file("ssl.key")

class Tools():
    def getNick(self, session):
        _, _, nick = session['Info']
        return nick

User = {
    "id": "",
    "ip": "",
    "name": "",
    "login": False
}

ALLOWED_EXTENSIONS = {"mp4"}
UPLOAD_FOLDER = "/var/www/vid.onpool.kr/public_html"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def makeUserDict(id='', ip='', login=False):
    _temp = User.copy()
    _temp['id'] = id
    _temp['ip'] = ip
    _temp['login'] = login
    return _temp


tool = Tools()


def event_logger(string, type='web'):
    try:
        open("logs/%s/%s.txt" % (type, datetime.now().strftime("%Y-%m-%d")), "a", encoding="UTF-8") \
            .write(string+"\n")
    except Exception as ex:
        print(" --- 로깅시스템에 문제가 있습니다. ---")
        print(ex)


@app.errorhandler(404)
def page_not_found(e):
    return render_template_string(
        gSet.html.error,
        code="404 Not Found",
        message_one="요청하신 페이지를 찾을 수 없습니다.",
        message_two="주소를 다시 확인하시고 다시 요청하시기 바랍니다."
    )


@app.errorhandler(500)
def internal_error(e):
    return render_template_string(
        gSet.html.error,
        code="500 Internal Server Error",
        message_one="서버의 내부적 문제로 페이지를 표시할 수 없습니다.",
        message_two="현재 상태가 지속되면 "+Markup("<a href='https://discord.gg/7YxYAv8' target='_blank'>여기</a>")+"로 문의주시기 바랍니다.".strip('"')
    )


# --- File hosts ---
@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(gSet.htmlDir + "/css/", filename)


@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory(gSet.htmlDir + "/js/", filename)


@app.route("/img/<path:filename>")
def img(filename):
    return send_from_directory(gSet.htmlDir + "/img/", filename)


@app.route("/fonts/<path:filename>")
def fonts(filename):
    return send_from_directory(gSet.htmlDir + "/fonts/", filename)


@app.route("/make_info")
def make_info():
    session["Info"] = "bc1916", "_PWHASH__PWHASH__PWHASH__PWHASH__PWHASH__PWHASH__PWHASH__PWHASH_", "이은학"
    session['User'] = makeUserDict(id="bc1916", ip=request.environ['REMOTE_ADDR'], login=True)
    return "OK"


@app.route("/my_page", methods=["GET"])
def mypage():
    print(session)
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"
    if not session['User']['login']: return "<meta http-equiv='refresh' content='0; url=/login' />"

    page = request.args.get("col")
    if page in ["summary", "mypage", "point"]:
        return render_template_string(open("html/mypage.html", encoding='UTF-8').read(), version=gSet.version, now_page=page, session=session)

    page = "summary"
    return redirect("my_page?col={}".format(page))


@app.route("/api/me/my_point_detail")
def my_point_detail():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"
    if not session['User']['login']: return "<meta http-equiv='refresh' content='0; url=/login' />"

    return json.dumps({"code":"SUC", "data": [ ["2017-01-14 15:38:21", "기본지급", ""] ]})

app.run(gSet.webhost, gSet.webport, debug=True, threaded=True)#, 443, ssl_context = ('ssl.crt', 'ssl.key'), debug=True, threaded=True)
