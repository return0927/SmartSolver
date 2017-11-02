import hashlib
from urllib.parse import parse_qs

import db
import general_settings
from flask import *

gSet = general_settings.Settings()
DB = db.DB()

app = Flask(__name__)
app.config['SECRET_KEY'] = gSet.hostKey
encrypt = lambda x: hashlib.sha256(x.encode()).hexdigest().upper()


@app.route("/")
def root():
    return gSet.html.root


@app.route("/login", methods=["GET", "POST"])
def login():
    isPost = request.method == "POST"

    if not isPost:
        return gSet.html.login

    else:
        postData = parse_qs(request.get_data().decode())
        _id = postData["id"][0]
        _pw = encrypt(postData["pw"][0])

    result, info = DB.getAccount(_id, _pw)

    if result:
        return "오류가 발생했습니다.<br/><br/>%s"%info
    else:
        if len(info):
            name = info[0][0]
            session["Info"] = _id, _pw, name

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
        postData = parse_qs(request.get_data().decode())
        pw, pw_confirm = encrypt(postData['pw'][0]), encrypt(postData['pw-confirm'][0])

        if pw != pw_confirm: return "<script>alert('비밀번호, 비밀번호 확인이 일치하지 않습니다.');history.go(-1);</script>"
        del pw_confirm

        _name = postData['name'][0]
        _birthday = postData['birthday'][0]
        _grade = int(postData['school'][0])*10 + int(postData['grade'][0])
        _email = postData['email'][0]
        _id = postData['id'][0]
        _pw = pw
        del pw, postData

        if DB.checkIDExist(_id): return "<script>alert('사용할 수 없는 아이디입니다!');history.go(-1);</script>"
        if DB.checkEmailExist(_email): return "<script>alert('이미 등록되어있는 이메일입니다!');history.go(-1);</script>"

        result = DB.addUser(_id, _pw, _name, _birthday, _grade, _email)
        if result:
            return "오류가 발생하였습니다!<br /><br />%s"%result

        return "<script>alert('가입에 성공하였습니다!');location.href='/login';</script>"

    else:
        return gSet.html.register



@app.route("/css/<path:filename>")
def css(filename):
    print(filename)
    return send_from_directory(gSet.htmlDir + "/css/", filename)


@app.route("/img/<path:filename>")
def img(filename):
    print(filename)
    return send_from_directory(gSet.htmlDir + "/img/", filename)


app.run(gSet.host, gSet.port)
