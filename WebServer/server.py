import hashlib
import json
import validater
import string
import random
from urllib.parse import parse_qs

import db
import general_settings
from flask import *

gSet = general_settings.Settings()
DB = db.DB()

app = Flask(__name__)
app.config['SECRET_KEY'] = gSet.hostKey
encrypt = lambda x: hashlib.sha256(x.encode()).hexdigest().upper()


class Tools():
    def getNick(self, session):
        _, _, nick = session['Info']
        return nick

tool = Tools()


@app.route("/")
def root():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    return gSet.html.root%(tool.getNick(session))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/' />"

    ip = request.environ["REMOTE_ADDR"]
    isPost = request.method == "POST"

    if not isPost:
        return gSet.html.login

    else:
        postData = parse_qs(request.get_data().decode())
        _id = postData["id"][0]
        _pw = encrypt(postData["pw"][0])

    result, info = DB.getAccount(_id, _pw, ip)

    if result:
        return "오류가 발생했습니다.<br/><br/>%s"%info
    else:
        if len(info):
            name = info[0][0]
            session["Info"] = _id, _pw, name

            if DB.submitRecentIP(_id, ip): return "<script>alert('서버에 오류가 발생하였습니다. \nCODE:L_UPD_Ad');history.go(-1);</script>"

            return "<script>alert('환영합니다, %s님!');location.href='/';</script>"%name
        else:
            return "<script>alert('아이디 혹은 비밀번호를 확인해주세요.');history.go(-1);</script>"


@app.route("/logout")
def logout():
    del session["Info"]
    return "<script>alert('로그아웃 되었습니다.');location.href='/';</script>"


@app.route("/register", methods=["GET", "POST"])
def register():
    isPost = request.method == "POST"

    if isPost:
        ip = request.environ['REMOTE_ADDR']
        try:
            postData = parse_qs(request.get_data().decode())
            pw, pw_confirm = encrypt(postData['pw'][0]), encrypt(postData['pw-confirm'][0])

            if pw != pw_confirm: return "<script>alert('비밀번호, 비밀번호 확인이 일치하지 않습니다.');history.go(-1);</script>"
            del pw_confirm


            # --- Parse data --- #
            _name = postData['name'][0]
            _birthday = postData['birthday'][0]
            _grade = int(postData['school'][0])*10 + int(postData['grade'][0])
            _email = postData['email'][0]
            _id = postData['id'][0]
            _pw = pw
            del pw, postData

            # --- Check Validation --- #
            if DB.checkIDExist(_id, ip): return "<script>alert('사용할 수 없는 아이디입니다!');history.go(-1);</script>"
            if DB.checkEmailExist(_email, ip): return "<script>alert('이미 등록되어있는 이메일입니다!');history.go(-1);</script>"
            if _grade not in [1, 2, 3, 11, 12, 13, 21, 22, 23]: return "<script>alert('학교/학년을 다시 한 번 확인해주세요.');history.go(-1);</script>"

            err, data = validater.birthday(_birthday)
            if err: return "<script>alert('%s');history.go(-1);</script>"%data

            err, data = validater.email(_email)
            if err: return "<script>alert('%s');history.go(-1);</script>"%data


            # --- IP Info Update --- #
            result = DB.addUser(_id, _pw, _name, _birthday, _grade, _email, ip)
            if result:
                return "오류가 발생하였습니다!<br /><br />%s"%result

            return "<script>alert('가입에 성공하였습니다!');location.href='/login';</script>"
        except Exception as ex:
            return "<script>alert(\"입력한 정보를 다시 한 번 확인해주세요.\"); history.go(-1);</script>"
    else:
        return gSet.html.register


# --- API Controller ---


"""
교학사교과서, 금성교과서, 동아교과서, 미래엔교과서, 비상교과서, 신사고교과서, 지학사교과서, 천재(이)교과서
라이트쎈, 쎈, 일품, RPM, 블랙라벨, 기본정석, 실력정석, 마플수능기출, 자이스토리(고3)
"""


@app.route("/api/textbooks", methods=["GET"])
def getTextbookDB():
    ip = request.environ['REMOTE_ADDR']

    keys = request.args.get("key")
    curr = request.args.get("curr")

    if keys:
        try:
            result, data = DB.getTextBooks(ip, keys, curr if curr else None)
            if result: return "{'result':'%s'}"%data
            return json.dumps({"result":data})
        except Exception as ex:
            return "{'result':'%s'}"%str(ex)

    return "{'result':'Invalid Request'}"


@app.route("/api/curriculumn", methods=["GET"])
def getCurriculumn():
    ip = request.environ['REMOTE_ADDR']

    try:
        result, data = DB.getCurriculumn(ip)
        data = [x[0] for x in data]

        if result: return "{'result':'%s'}"%data
        return json.dumps({"result":data})
    except Exception as ex:
        print(ex)
        return "{'result':'%s'}"%str(ex)


@app.route("/api/bookModifiedYear", methods=["GET"])
def getBookModifiedYear():
    ip = request.environ['REMOTE_ADDR']

    curr = request.args.get("curr")
    book = request.args.get("book")

    if not (curr and book):
        return "{'result':'Invalid Request'}"

    try:
        result, data = DB.getBookModifiedYear(curr, book, ip)
        data = data[0]

        if result: return "{'result':'%s'}"%data
        return json.dumps({"result":data})
    except Exception as ex:
        print(ex)
        return "{'result':'%s'}"%str(ex)


@app.route("/api/bookPublisher", methods=["GET"])
def getBookPublisher():
    ip = request.environ['REMOTE_ADDR']

    curr = request.args.get("curr")
    book = request.args.get("book")

    if not (curr and book):
        return "{'result':'Invalid Request'}"

    try:
        result, data = DB.getBookPublisher(curr, book, ip)
        data = data[0]

        if result: return "{'result':'%s'}"%data
        return json.dumps({"result":data})
    except Exception as ex:
        print(ex)
        return "{'result':'%s'}"%str(ex)


@app.route("/api/bookNotice", methods=["GET"])
def getBookNotice():
    ip = request.environ['REMOTE_ADDR']

    curr = request.args.get("curr")
    book = request.args.get("book")

    if not (curr and book):
        return "{'result':'Invalid Request'}"

    try:
        result, data = DB.getBookNotice(curr, book, ip)
        data = data[0]

        if result: return "{'result':'%s'}"%data
        return json.dumps({"result":data})
    except Exception as ex:
        print(ex)
        return "{'result':'%s'}"%str(ex)


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


# --- Player ---
@app.route("/video/flowplayer/<path:filename>")
def flowplayer(filename):
    return send_from_directory(gSet.htmlDir + "/players/", filename)


app.run(gSet.host, gSet.port)
