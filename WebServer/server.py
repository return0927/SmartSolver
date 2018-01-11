import hashlib
import json
import validater
import string
import random
import threading
from urllib.parse import parse_qs
from datetime import datetime
from OpenSSL import SSL

import db
import general_settings
import email_verification
from flask import *

gSet = general_settings.Settings()
DB = db.DB()

app = Flask(__name__)
app.config['SECRET_KEY'] = gSet.hostKey
encrypt = lambda x: hashlib.sha256(x.encode()).hexdigest().upper()

context = SSL.Context(SSL.SSLv23_METHOD)
context.use_certificate_file("ssl.crt")
context.use_privatekey_file("ssl.key")

class Tools():
    def getNick(self, session):
        _, _, nick = session['Info']
        return nick

User = {
    "id": "",
    "ip": "",
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


@app.before_request
def req():
    url = request.url
    method = request.method
    ip = request.environ['REMOTE_ADDR']
    logon = "Info" in session.keys()
    info = str(session['Info']) if logon else "None"

    if "User" not in session.keys(): session['User'] = makeUserDict(ip=ip)

    event_logger("\t".join([datetime.now().strftime("%Y-%m-%d_%H:%M:%S"), url, method, ip, str(logon), info]))

    #print(threading.get_ident())


@app.route("/")
def root():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"
    if not session['User']['login']: return "<meta http-equiv='refresh' content='0; url=/login' />"

    return send_from_directory("html", "index.html")


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
            email_verf = info[0][1]

            if email_verf != "VERIFIED": return "<script>alert('이메일 인증을 하신 후에 사용하실 수 있습니다.');location.href='/verify';</script>"

            session["Info"] = _id, _pw, name

            if DB.submitRecentIP(_id, ip): return "<script>alert('서버에 오류가 발생하였습니다. \nCODE:L_UPD_Ad');history.go(-1);</script>"

            session['User']['id'] = _id
            session['User']['login'] = True
            return "<script>alert('환영합니다, %s님!');location.href='/';</script>"%name
        else:
            return "<script>alert('아이디 혹은 비밀번호를 확인해주세요.');history.go(-1);</script>"


@app.route("/verify", methods=["GET"])
def verify_email():
    code = None
    try: code = request.args.get("code")
    except: pass

    if code is None:
        return gSet.html.verify
    elif len(code) != 32:
        return gSet.html.verify
    elif len(code) == 32:
        err, data = DB.verifyCode(code, request.environ['REMOTE_ADDR'])
        print(err, data)
        if err: return "<script>alert('코드 인증 중 오류가 발생하였습니다.');location.history(-1);</script>"
        else:
            if data is False:
                return "<script>alert('인증코드를 입력해주세요.');</script>"
            else:
                return "<script>alert('성공적으로 인증이 완료되었습니다.');location.href='/';</script>"

    return gSet.html.verify

@app.route("/go")
def go():
    return "<script>location.href='/login';</script>"


@app.route("/logout")
def logout():
    try:
        del session["Info"]
        del session['User']
        return "<script>alert('로그아웃 되었습니다.');location.reload();</script>"
    except:
        return "<script>location.href='/go';</script>"


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
            #_code = postData['code'][0]
            _pw = pw
            del pw, postData

            # --- Check Validation --- #
            if DB.checkIDExist(_id, ip): return "<script>alert('사용할 수 없는 아이디입니다!');history.go(-1);</script>"
            if any(word in _id.lower() for word in ['admin', 'webmaster', 'onpool', 'sunsky']): return "<script>alert('사용할 수 없는 아이디입니다!');history.go(-1);</script>"
            if DB.checkEmailExist(_email, ip): return "<script>alert('이미 등록되어있는 이메일입니다!');history.go(-1);</script>"
            if _grade not in [1, 2, 3, 11, 12, 13, 21, 22, 23]: return "<script>alert('학교/학년을 다시 한 번 확인해주세요.');history.go(-1);</script>"
            #if len(_code) != 64: return "<script>alert('올바르지 않은 인증키입니다!');history.go(-1);</script>"
            #if not DB.checkBetaCode(_code, ip): return "<script>alert('올바르지 않은 인증키입니다!');history.go(-1);</script>"

            err, data = validater.birthday(_birthday)
            if err: return "<script>alert('%s');history.go(-1);</script>"%data

            err, data = validater.email(_email)
            if err: return "<script>alert('%s');history.go(-1);</script>"%data

            _code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            # --- IP Info Update --- #
            result = DB.addUser(_id, _pw, _name, _birthday, _grade, _email, ip, _code)
            if result:
                return "오류가 발생하였습니다!<br /><br />%s"%result

            #err, data = validater.sendVerf(_email, _code)
            #print(err, data)

            threading.Thread(target=email_verification.send, args=(_email, _code,)).start()
            return "<script>alert('가입에 성공하였습니다!\\n이메일 인증을 진행한 후 로그인해주세요.');location.href='/login';</script>"
            # return "<script>alert('가입에 성공하였습니다!\\n');location.href='/login';</script>"
        except Exception as ex:
            print("Error on Registration data verification : %s")
            raise ex
            # return "<script>alert(\"입력한 정보를 다시 한 번 확인해주세요.\"); history.go(-1);</script>"
    else:
        return gSet.html.register


# --- Admin Panel ---
@app.route("/panel", methods=["GET"])
def admin_panel():
    if not session['User']['id'] in gSet.admins: return page_not_found(None)
    return send_from_directory('html/', 'panel.html')


@app.route("/panel/api/questions", methods=["GET"])
def get_all_questions():
    if not session['User']['id'] in gSet.admins: return page_not_found(None)

    count = request.args.get("c")
    print(count)
    if count is None: count = 20
    err, data = DB.getAllQuestions(limit=count)
    if err: return json.dumps({"code":"ERR"})

    ret = []
    for pid, qid, sid, date, t, status, message in data:
        err, [bookid, page, number] = DB.getProblemInfo(qid)
        if err: return json.dumps({"code": "ERR"})

        err, [currid, bookname, year] = DB.getBookInfo(bookid)
        if err: return json.dumps({"code": "ERR"})

        err, curr = DB.getSub(currid)
        if err: return json.dumps({"code": "ERR"})

        # 처리번호(qid)	등록자(sid)	등록일시(date+time)	과목(curr)	교재(bookname+year)	페이지(page)	번호(number)	상태(status) 메세지(message)
        ret.append([pid, qid, sid, date+t.strftime(" %H:%M:%S"), curr, "{}({})".format(bookname, year), page, number, status, message])

    return json.dumps({"code":"SUC", "data": ret})

@app.route("/panel/api/videos", methods=["GET"])
def get_all_videos():
    if not session['User']['id'] in gSet.admins: return page_not_found(None)

    count = request.args.get("c")
    print(count)
    if count is None: count = 20
    err, data = DB.getAllVideos(limit=count)
    if err: return json.dumps({"code":"ERR"})

    ret = []
    for pid, url, tutor, hit in data:
        err, [bookid, page, number] = DB.getProblemInfo(pid)
        if err: return json.dumps({"code": "ERR"})

        err, [currid, bookname, year] = DB.getBookInfo(bookid)
        if err: return json.dumps({"code": "ERR"})

        err, curr = DB.getSub(currid)
        if err: return json.dumps({"code": "ERR"})

        # 질문번호(pid) 영상주소(url)   과목(curr)   책정보(bookname+year)  페이지(page)   번호(number)  강사(tutor)   조회수(hit)
        ret.append([pid, url, curr, "{}({})".format(bookname, year), page, number, tutor, hit])

    return json.dumps({"code": "SUC", "data": ret})

@app.route("/panel/api/problems", methods=["GET"])
def get_all_problems():
    if not session['User']['id'] in gSet.admins: return page_not_found(None)

    count = request.args.get("c")
    print(count)
    if count is None: count = 20
    err, data = DB.getAllProblems(limit=count)
    if err: return json.dumps({"code":"ERR"})

    ret = []
    for pid, bid, page, number in data:
        err, [currid, bookname, year] = DB.getBookInfo(bid)
        if err: return json.dumps({"code": "ERR"})

        err, curr = DB.getSub(currid)
        if err: return json.dumps({"code": "ERR"})

        ret.append([pid, curr, "{}({})".format(bookname, year), page, number])

    return json.dumps({"code":"SUC", "data": ret})

@app.route("/panel/api/make", methods=["GET", "POST"])
def make_problem():
    if not session['User']['id'] in gSet.admins: return page_not_found(None)

    if request.method == "POST":
        try:
            curr = request.form.get("curr")
            bookname = request.form.get("bookname")
            year = request.form.get("year")
            page = request.form.get("page")
            number = request.form.get("number")

            err, data = DB.makeProblem(curr, bookname, year, page, number)
            if err: return """
            <script>
                prompt("문제를 만드는 중 오류가 생겼습니다.", "{}";
                location.history(-1);
            </script>
            """.format(data.replcae("\n"," "))

            return """
            <script>
                prompt("성공적으로 문제를 만들었습니다! 아래의 문제번호를 확인해주세요.", "{}");
                window.close();
            </script>
            """.format(data)
        except Exception as ex:
            return json.dumps({"code":"ERR", "data":str(ex)})
    elif request.method == "GET":
        return """
    <!doctype html>
    <script type="text/javascript" src="/js/jquery.min.js"></script>
    <script type="text/javascript" src="/js/panel_make.js"></script>
    <title>Upload new File</title>
    <h1>새 질문 만들기</h1>
    <form action="" method=post>
        ProblemID: <input type=text value="자동입력" disabled /><br />
        과목번호: <select id="subject" name="curr" onchange="getBook(this);">
                <option disabled>2009개정 교육과정</option>
                <option value="1">수학I</option>
                <option value="2">수학II</option>
                <option value="3">미적분I</option>
                <option value="4">미적분II</option>
                <option value="5">확률과통계</option>
                <option value="6">기하와벡터</option>
                <option disabled>2015개정 교육과정</option>
                <option value="7">수학</option>
                <option value="8">수학(상)</option>
                <option value="9">수학(하)</option>
            </select><br />
        교재: <select id="book_series" onload="getYears(this);" onchange="getYears(this);" name="bookname">
            </select><br />
        출판연도: <select id="year" name="year">
                </select><br />
        페이지(챕터): <input type="text" name="page" /><br />
        문항번호: <input type="text" name="number" /><br />
        <input type=submit value=Upload />
    </form>
    """

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/panel/api/upload", methods=["GET","POST"])
def upload_video():
    if not session['User']['id'] in gSet.admins: return page_not_found(None)

    if request.method == "POST":
        id = session['User']['id']

        file = request.files['file']
        print(file)
        vid = request.form.get("vid")
        pid = request.form.get("pid")
        print(vid)

        if not vid.isnumeric(): return json.dumps({"code":"ERR"})

        if file and allowed_file(file.filename):
            m = hashlib.sha256()
            m.update( str((int(vid)+38)**2).encode() )
            filename = m.hexdigest() + ".mp4"
            print(vid, filename)
            d = file.save(app.config['UPLOAD_FOLDER']+"/"+filename)
            print(d)
            print("success")

            err, data = DB.insertVideo(id, filename[:-4], pid, session['User']['id'], request.environ['REMOTE_ADDR'])
            if err: return """
                        <script>
                            prompt('업로드에 실패하였습니다.','{}');
                            window.close();
                        </script>
                        """.format(data.replace("\n"," "))
            err, data = DB.updateStatus(pid)
            if err: return """
                        <script>
                            prompt('업로드는 성공하였으나, 자동처리에 문제가 있습니다..','{}');
                            window.close();
                        </script>
                        """.format(filename[:4]+"|"+data.replace("\n"," "))

            return """
            <script>
                prompt('성공적으로 업로드되었습니다! 아래의 영상번호 해쉬를 기록해주세요.','{}');
                window.close();
            </script>
            """.format(filename[:-4])

        return json.dumps({"code":"ERR"})

    elif request.method == "GET":
        return """
    <!doctype html>
    <title>새 영상 업로드</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
        FILE: <input type=file name=file><br />
        ProblemID: <input type=text name=pid> <br />
        VideoID: <input type=text name=vid> (해쉬값이 아닌 정수로 입력해주세요.)<br />
        <input type=submit value=Upload>
    </form>
    """


@app.route("/panel/api/editMessage", methods=["POST"])
def panel_edit_message():
    qid = request.form.get("qid")
    msg = request.form.get("msg")

    err, data = DB.updateQuestionMessage(qid, msg, session['User']['id'], request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR", "data": data})
    return json.dumps({"code":"SUC"})


@app.route("/panel/api/delQuestion", methods=["POST"])
def panel_del_question():
    qid = request.form.get("qid")

    err, data = DB.deleteQuestion(qid, session['User']['id'], request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR", "data": data})
    return json.dumps({"code":"SUC"})


@app.route("/panel/api/markQuestion", methods=["POST"])
def panel_mark_question():
    qid = request.form.get("qid")

    err, data = DB.markQuestion(qid, session['User']['id'], request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR", "data": data})
    return json.dumps({"code":"SUC"})


@app.route("/panel/api/delProblem", methods=["POST"])
def panel_del_problem():
    pid = request.form.get("pid")

    err, data = DB.deleteProblem(pid, session['User']['id'], request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR", "data": data})
    return json.dumps({"code":"SUC"})


@app.route("/panel/api/delVideo", methods=["POST"])
def panel_del_video():
    pid = request.form.get("pid")

    err, data = DB.deleteVideo(pid, session['User']['id'], request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR", "data": data})
    return json.dumps({"code":"SUC"})

# --- Function ---
""""@app.route("/submit", methods=["POST"])
def submitQuestion():
    ip = request.environ["REMOTE_ADDR"]

    data =  parse_qs(request.get_data().decode())

    curr = data['curr'][0]
    book = data['book'][0]
    year = data['year'][0]
    number = data['number'][0]
    question = data['question'][0]

    try: bookId = getTbookId(curr, book, year)
    except Exception as ex:
        print(ex)
        return "<script>alert('오류가 발생했습니다!');location.reload();</script>"

    err, data = DB.submitmyQuestion(session['Info'][0], bookId, question, number, ip)
    if err:
        print(data)
        return "<script>alert('오류가 발생했습니다!');location.reload();</script>"

    return "<script>alert('등록되었습니다!');location.reload();</script>"
"""

@app.route("/submit", methods=["POST"])
def submitQuestion():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    err, limit = DB.getMyDayRateLimit(session['User'], "AUTOMATION:"+request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code": "ERR", "data": limit})

    err, count = DB.getMyQuestionTodayCount(session['User'], 'AUTOMATION:'+request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code": "ERR", "data": count})

    print("Day Limitation",count, limit)

    if count >= limit:
        return json.dumps({"code": "ERR", "data": "하루한도 초과 ({}개)".format(limit)})

    now_point = get_my_point(simple=True, user=session['User']['id'])[0]
    print(now_point, gSet.question_cost)
    if now_point < gSet.question_cost:
        return json.dumps({"code":"ERR", "data": "포인트가 부족합니다! (개당 {}포인트)".format(gSet.question_cost)})

    subject = request.form.get("subject")
    bookseries = request.form.get("bookseries")
    year = request.form.get("year")
    page = request.form.get("page")
    q_no = request.form.get("q_no")

    if not year.isnumeric(): return json.dumps({"code":"ERR"})
    if not q_no.isnumeric(): return json.dumps({"code":"ERR"})
    if "-" in subject + bookseries + year + page + q_no: return json.dumps({"code":"ERR"})

    err, data = DB.submitmyQuestion(session['User']['id'], subject, bookseries, year, page ,q_no, request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR", "data": data})
    else: return json.dumps({"code":"SUC", "data": data})


# --- API Controller ---
@app.route("/api/get_bookseries", methods=["GET"])
def get_bookseries():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    err, data = DB.getBookSeries(request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR"})
    else: return json.dumps({"code":"SUC", "data": [ x[0] for x in data ]})


@app.route("/api/get_year", methods=["POST"])
def get_year():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    subject = request.form.get("subject")
    book = request.form.get("bookseries")

    err, data = DB.getYear(subject, book, request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR"})
    else:
        err, msg = DB.getBookMessage(book)
        if err: return json.dumps({"code":"ERR"})
        else: return json.dumps({"code":"SUC", "data": [ x[0] for x in data], "msg":msg})


@app.route("/api/me/my_point", methods=["GET"])
def get_my_point(simple=False, local=True, user=''):
    if local:
        err, data = DB.get_point(user, request.environ["REMOTE_ADDR"])
        if simple:
            if err:
                return None
            else:
                return data

    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    user = session["User"]["id"]

    err, data = DB.get_point(user, request.environ["REMOTE_ADDR"])
    if err: return json.dumps({"code":"ERR"})
    else: return json.dumps({"code":"SUC", "data": data})


@app.route("/api/me/questions", methods=["GET"])
def get_my_questions():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    err, data = DB.getMyQuestion(session['User'], request.environ['REMOTE_ADDR'])
    if err: return json.dumps({"code":"ERR"})
    else:
        ret = []
        for pid, date, status, message in data:
            err, [bookid, page, number] = DB.getProblemInfo(pid)
            if err: return json.dumps({"code":"ERR"})

            err, data = DB.getVideo(pid)
            if err: url = 'javascript: alert("오류로 인해 영상을 불러오지 못했습니다.");'
            else:
                if data is False: url = ''
                else: url = data

            err, [currid, bookname, year] = DB.getBookInfo(bookid)
            if err: return json.dumps({"code":"ERR"})

            err, curr = DB.getSub(currid)
            if err: return json.dumps({"code":"ERR"})

            ret.append([date, curr, "{}({})".format(bookname, year), page, number, status, message, url])
        return json.dumps({"code":"SUC", "data": ret})


@app.route("/api/me/questions_today", methods=["GET"])
def get_my_today_questions():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    err, data = DB.getMyQuestion(session['User'], request.environ["REMOTE_ADDR"], timestr='current_date')

    if err: return json.dumps({"code":"ERR"})
    else: return json.dumps({"code":"SUC", "data": data})


@app.route("/api/me/day_rate_limit", methods=["GET"])
def get_my_date_rate():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    err, data = DB.getMyDayRateLimit(session['User'], request.environ["REMOTE_ADDR"])

    if err: return json.dumps({"code":"ERR"})
    else: return json.dumps({"code":"SUC", "data": data})


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
@app.route("/video/flowplayer/play", methods=["GET"])
def fplayer():
    if not "Info" in session.keys(): return "<meta http-equiv='refresh' content='0; url=/login' />"

    ip = request.environ["REMOTE_ADDR"]

    try:
        vid = request.args.get("vid")
        id, pw, name = session["Info"]
        print(id+name+ip)
        token = encrypt(id+name+ip+str(vid))
        print(token)

        return gSet.html.flowplayer%(str(vid), token, str(vid))

    except Exception as ex:
        print(ex)
        return "<script>alert('플레이중 오류가 생겼습니다!');history.go(-1);</script>"

@app.route("/video/flowplayer/<path:filename>")
def flowplayer(filename):
    return send_from_directory(gSet.htmlDir + "/players/", filename)

@app.route("/video/flowplayer/img/<path:filename>")
def flowplayer_IMG(filename):
    return send_from_directory(gSet.htmlDir + "/players/img/", filename)


# --- Player Support ---
@app.route("/sup/logger", methods=["POST"])
def logger():
    ip = request.environ['REMOTE_ADDR']

    try:
        data = parse_qs(request.get_data().decode())
        vid = data['videoID'][0]
        token = data['authKey'][0]
        id, pw, name = session["Info"]

        if encrypt(id + name + ip + str(vid)) == token:
            return "{'code':'success'}"
        else:
            return "{'code':'fail'}"
    except Exception as ex:
        print(ex)
        return "{'code':'fail'}"


@app.route("/sup/checkValidation", methods=["POST"])
def validation():
    ip = request.environ['REMOTE_ADDR']

    try:
        data = parse_qs(request.get_data().decode())
        vid = data['videoID'][0]
        token = data['authKey'][0]
        id, pw, name = session["Info"]

        if encrypt(id + name + ip + str(vid)) == token:
            return "{'code':'right'}"
        else:
            return "{'code':'fail'}"
    except Exception as ex:
        print(ex)
        return "{'code':'fail'}"


app.run(gSet.webhost, gSet.webport, debug=False, threaded=True)#, 443, ssl_context = ('ssl.crt', 'ssl.key'), debug=True, threaded=True)
