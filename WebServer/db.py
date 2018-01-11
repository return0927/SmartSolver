import psycopg2
import re
import json
import requests
import random, string
import validater
import threading
import general_settings
import email_verification
from datetime import datetime

rand = lambda len: ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(len)).upper()

class DB:
    def __init__(self):
        self.gSet = general_settings.Settings()

        self.host = self.gSet.host
        self.port = self.gSet.port
        self.user = self.gSet.user
        self.pw = self.gSet.pw
        self.db = self.gSet.db

        self.conn = None
        self.cursor = None
        self.logfile = "logs/db/%s.txt"

        self.connDict = {}
        self.curDict = {}

        self.getConn()

    def send_email(self, email, title, message):
        threading.Thread(target=email_verification._send_notify, args=(email, title, message, )).start()

    def _send_webhook(self, title, content, user, url, ip, colour=3447003):
        data = {
            "username": "온풀 웹서비스",
            "avatar_url": "",
            "tts": False,
            "content": "",
            "author": {
                "name": "",
                "icon_url": "",
            },
            "embeds": [
                {
                    "color": colour,
                    "title": "{}".format(title),
                    "description": "{}".format(content),
                    "url": "http://onpool.kr",
                    "fields": [
                        {"name": "/ {} /".format(user), "value": "URL: {}\nIP: {}\nTIME:{}".format(url, ip, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")), "inline": False},
                    ],
                    "footer": {
                        'text': "ⓒ 이은학 (이은학#9299) \\ Github @R3turn0927 \\ KakaoTalk @bc1916"
                    }
                }
            ]
        }

        return requests.post("https://discordapp.com/api/webhooks/400916071290372106/_BGMidyEj35vyLBzBQ2k-ILjBrVCVJDtpHBA940EznQDjO-eIqlTxhNEpNVkBGgoSILH", data=json.dumps(data), headers={"Content-type":"multipart/form-data"}).text


    def hardfilter(self, string, r=re.compile("[a-zA-Z0-9]{1,}")):
        print(string)
        res = r.match(string)
        if res is None: return False
        if string == res.group(): return True
        return False


    def getConn(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pw,
            database=self.db
        )
        self.conn.autocommit = True

        return self.conn

    def writeLog(self, _ip, query):
        open(self.logfile%datetime.now().strftime("%Y-%m-%d"), "a", encoding="UTF-8")\
            .write("%s\t%s\t%s\n"%(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"), _ip, query))

    def getCursor(self):
        thread_id = threading.get_ident().__int__()

        if not thread_id in self.connDict.keys():
            self.connDict[thread_id] = self.getConn()

        if thread_id not in self.curDict.keys():
            self.curDict[thread_id] = self.connDict[thread_id].cursor()

        return self.curDict[thread_id]

    def checkIDExist(self, id, _ip):
        if not self.hardfilter(id): return True
        cur = self.getCursor()

        query = 'SELECT "id" FROM users WHERE id=\'%s\'' % id
        self.writeLog(_ip, query)

        cur.execute(query)

        _data = cur.fetchall()
        return _data

    def checkEmailExist(self, email, _ip):
        err, _ = validater.email(email)
        if err: return True

        cur = self.getCursor()

        query = 'SELECT "email" FROM users WHERE email=\'%s\'' % email
        self.writeLog(_ip, query)

        cur.execute(query)
        _data = cur.fetchall()
        return _data

    def addUser(self, _id, _pw, _name, _bir, _gra, _email, _ip, _code):
        if not self.hardfilter(_id): return "Invalid Query"
        if validater.email(_email)[0]: return "Invalid Query"

        cur = self.getCursor()
        try:
            cur.execute('INSERT INTO users VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (
                _id, _pw, _name, _gra, _bir, _email, _code, _ip, _ip))
            self.conn.commit()
            return False
        except Exception as ex:
            return str(ex)

    def verifyCode(self, code, ip):
        cur = self.getCursor()
        try:
            query = 'SELECT \'T\' FROM users WHERE email_verified=\'{}\';'.format(code)
            self.writeLog(ip, query)

            cur.execute(query)
            ret = len(cur.fetchall())

            if ret:
                query = 'UPDATE users SET email_verified = \'VERIFIED\' WHERE email_verified=\'{}\';'.format(code)
                self.writeLog(ip, query)

                cur.execute(query)
                return [False, True]
            else:
                return [False, False]
        except Exception as ex:
            return [True, str(ex)]

    def submitRecentIP(self, _id, _ip):
        cur = self.getCursor()
        try:
            query = 'UPDATE users SET recent_ip = \'%s\' WHERE id = \'%s\';'%(_ip, _id)
            self.writeLog(_ip, query)

            cur.execute(query)
            self.conn.commit()
            return False
        except Exception as ex:
            return str(ex)

    # TODO: Regex Check [a-zA-Z0-9]{1,}
    def getAccount(self, _id, _pw, _ip):
        if not self.hardfilter(_id): return [True, "Invalid Query"]

        cur = self.getCursor()
        try:
            query = 'SELECT name, email_verified FROM users WHERE id=\'%s\' and pw=\'%s\''%(_id,_pw)
            self.writeLog(_ip, query)

            cur.execute(query)
            result = cur.fetchall()
            print(result)

            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getBookSeries(self, ip, selection="*"):
        cur = self.getCursor()

        try:
            query = 'SELECT name FROM bookseries WHERE serviced=TRUE ;'
            self.writeLog(ip, query)

            cur.execute(query)

            result = cur.fetchall()
            return [False, sorted(result)]
        except Exception as ex:
            return [True, str(ex)]

    def getSubjId(self, subj, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT id FROM curriculum WHERE name=\'{}\';'.format(subj)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()[0]
            return [False, result]
        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getSub(self, subjid):
        cur = self.getCursor()

        try:
            query = 'SELECT name FROM curriculum WHERE id=\'{}\';'.format(subjid)
            #self.writeLog("LOCAL", query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0][0]]
        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getYear(self, subj, book, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT year FROM book WHERE bookname=\'{1}\' AND curr_id=\'{0}\';'.format(subj, book)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result]
        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getBook(self, subj, book, year):
        cur = self.getCursor()

        try:
            query = 'SELECT book_id FROM book WHERE bookname=\'{1}\' AND curr_id=\'{0}\' AND year=\'{2}\';'.format(subj, book, year)
            #self.writeLog("LOCAL", query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0][0]]
        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getBookMessage(self, book):
        cur = self.getCursor()

        try:
            query = 'SELECT message FROM bookseries WHERE name=\'{}\';'.format(book)
            #self.writeLog("LOCAL", query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0][0]]
        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getBookInfo(self, bid):
        cur = self.getCursor()

        try:
            query = 'SELECT curr_id, bookname, year FROM book WHERE book_id=\'{}\';'.format(bid)
            #self.writeLog("LOCAL", query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0]]
        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    # --- beta ---
    def checkBetaCode(self, code, ip):
        cur = self.getCursor()

        try:
            query = "SELECT code FROM codes WHERE allowed=1;"
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            result = [x[0] for x in result]

            if code not in result: return False
            query = "UPDATE codes SET allowed = 0 WHERE code='{}';".format(code)
            self.writeLog(ip, query)

            cur.execute(query)
            return True
        except Exception as ex:
            return False

    def getProblemId(self, book_id, page, number):
        cur = self.getCursor()

        try:
            query = 'SELECT problem_id FROM problem WHERE book_id=\'{}\' AND page=\'{}\' AND number=\'{}\';'.format(book_id, page, number)
            #self.writeLog("LOCAL", query)
            cur.execute(query)
            result = cur.fetchall()
            if len(result): return [False, result[0][0]]
            else: return [False, False]
        except Exception as ex:
            raise ex
            print(ex)
            return [True, str(ex)]

    def getProblemInfo(self, pid):
        cur = self.getCursor()

        try:
            query = 'SELECT book_id, page, number FROM problem WHERE problem_id=\'{}\';'.format(pid)
            #self.writeLog("LOCAL", query)
            cur.execute(query)
            result = cur.fetchall()
            if len(result): return [False, result[0]]
            else: return [False, False]
        except Exception as ex:
            raise ex
            print(ex)
            return [True, str(ex)]

    # --- Functional Features ---
    def getVideo(self, pid):
        cur = self.getCursor()

        try:
            query = 'SELECT url FROM solution_video WHERE problem_id=\'{}\';'.format(pid)
            #self.writeLog("LOCAL", query)
            cur.execute(query)
            result = cur.fetchall()
            if len(result): return [False, result[0][0]]
            else: return [False, False]
        except Exception as ex:
            raise ex
            print(ex)
            return [True, str(ex)]

    def checkDuplicated(self, pid, requester):
        cur = self.getCursor()

        try:
            query = 'SELECT status FROM question WHERE student_id=\'{}\' and problem_id=\'{}\';'.format(requester, pid)
            cur.execute(query)
            result = cur.fetchall()
            return [False, len(result)]
        except Exception as ex:
            raise ex
            print(ex)
            return [True, str(ex)]

    def submitmyQuestion(self, _requester, subj, bookseries, year, page, no, ip):
        cur = self.getCursor()

        try:
            duplicated = False
            err, bookid = self.getBook(subj, bookseries, year)
            if err: raise Exception(bookid)
            err, pid = self.getProblemId(book_id=bookid, page=page, number=no)
            if err: raise Exception(pid)

            if pid:
                print("Already Uploaded Question-Problem")
                err, ret = self.checkDuplicated(pid, _requester)
                if err: pass
                elif ret:
                        duplicated = True
            else:
                print("Adding New Question-Problem")
                query = 'INSERT INTO problem (book_id, page, number) VALUES ({}, \'{}\', {}) RETURNING problem_id;'.format(bookid, page, no)
                self.writeLog(ip, query)
                cur.execute(query)
                pid = cur.fetchall()[0][0]

            query = 'INSERT INTO question (problem_id, student_id) VALUES ({}, \'{}\') RETURNING question_id;'.format(pid, _requester)
            self.writeLog(ip, query)
            cur.execute(query)

            qid = cur.fetchall()[0][0]
            err, data = self.getVideo(pid)

            self._send_webhook("질문등록",
                               "Problem: {}\nQuestionID:{}\n교재번호: {}\n페이지(챕터): {}\n문항번호: {}\n신청자: {}\n\n새로운 질문이 접수되었습니다."
                               .format(pid, qid, bookid, page, no, _requester),
                               _requester, "DB.submitmyQuestion", ip
                               )
            if err: pass
            else:
                if data is False: pass
                else:
                    query = 'UPDATE question SET status = 1, message = \'자동답변\', p_time = current_date, p_time_ = now() WHERE question_id=\'{}\';'.format(qid)
                    self.writeLog("AUTOMATION", query)
                    cur.execute(query)

                    if not duplicated:
                        query = 'UPDATE users SET point = point - {} WHERE id=\'{}\';'.format(self.gSet.question_cost, _requester)
                        self.writeLog(ip, query)
                        cur.execute(query)

                    self._send_webhook("자동답변", "ProblemID: {}\nQuestionID: {}\n\n에 대한 해설영상이 자동으로 등록되었습니다.".format(pid, qid), _requester, "DB.submitmyQuestion", ip, colour=10539945)

            if duplicated: return [False, "중복질문으로 인해 포인트 차감없이 질문이 등록되었습니다."]
            else: return [False, "질문이 등록되었습니다."]
        except Exception as ex:
            raise ex
            return [True, str(ex)]

    # --- MyPage ---
    def getMyQuestion(self, User, ip, timestr="to_date('19700101','YYYYMMDD')"):
        cur = self.getCursor()

        try:
            query = 'SELECT problem_id, TO_CHAR(q_time, \'YYYY-MM-DD\'), status, message FROM question WHERE student_id=\'{}\' AND q_time >= {} ORDER BY question_id;'.format(User['id'], timestr)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            result.reverse()

            return [False, result]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getMyQuestionTodayCount(self, User, ip, timestr="current_date"):
        cur = self.getCursor()

        try:
            query = 'SELECT count(problem_id) FROM question WHERE student_id=\'{}\' AND q_time >= {}'.format(User['id'], timestr)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()[0][0]

            return [False, result]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def get_point(self, user, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT point FROM users WHERE id=\'{}\';'.format(user)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0]]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getMyDayRateLimit(self, User, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT daily_limit FROM users WHERE id=\'{}\';'.format(User['id'])
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0][0]]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    # --- Admin Panel ---
    def getAllQuestions(self, limit=20):
        cur = self.getCursor()

        try:
            print(limit)
            query = 'SELECT question_id, problem_id, student_id,TO_CHAR(q_time, \'YYYY-MM-DD\'), q_time_, status, message FROM question ORDER BY question_id DESC LIMIT {};'.format(limit)
            self.writeLog("ADMIN", query)

            cur.execute(query)
            result = cur.fetchall()

            return [False, result]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getAllVideos(self, limit=20):
        cur = self.getCursor()

        try:
            print(limit)
            query = 'SELECT problem_id, url, tutor, hit FROM solution_video ORDER BY problem_id;-- LIMIT={};'.format(limit)
            self.writeLog("ADMIN", query)

            cur.execute(query)
            result = cur.fetchall()

            return [False, result]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def getAllProblems(self, limit=20):
        cur = self.getCursor()

        try:
            print(limit)
            query = 'SELECT problem_id, book_id, page, number FROM problem ORDER BY problem_id;-- LIMIT={};'.format(limit)
            self.writeLog("ADMIN", query)

            cur.execute(query)
            result = cur.fetchall()

            return [False, result]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def insertVideo(self, id, vid, pid, nick, ip):
        cur = self.getCursor()

        try:
            query = 'INSERT INTO solution_video VALUES (\'{}\',\'/video/flowplayer/play?vid={}\',\'{}\',0);'.format(pid, vid, id)
            self.writeLog("ADMIN", query)

            cur.execute(query)

            self._send_webhook("영상 등록", "ProblemID: {}\nVideo Hash: {}\nUploader:{}\n\n새로운 영상이 업로드되었습니다.".format(pid, vid, id),
                               "{}".format(nick), "DB.insertVideo", ip, colour=3092790)

            return [False, None]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def updateStatus(self, pid):
        cur = self.getCursor()

        try:
            query = 'UPDATE question SET status=1, message=\'지연답변\', p_time = current_date, p_time_ = now() WHERE problem_id={} RETURNING (SELECT email FROM users WHERE id=question.student_id);;'.format(pid)
            self.writeLog("ADMIN", query)

            cur.execute(query)
            emails = [ x[0] for x in cur.fetchall()]

            for email in emails:
                self.send_email(email, "회원님의 질문에 대한 영상이 준비되었습니다.", """
                <p>회원님의 질문에 대한 해설영상이 방금 업로드되었습니다.</p>
                <br />
                <a target='_blank' href='http://onpool.kr/'>온풀 방문하기</a>""")

            return [False, None]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def makeProblem(self, subj, bookseries, year, page, no):
        cur = self.getCursor()

        try:
            err, bookid = self.getBook(subj, bookseries, year)
            if err: raise Exception("Error on Making Problem with bookid err: {}".format(bookid))
            print("Adding New Question-Problem")
            query = 'INSERT INTO problem (book_id, page, number) VALUES ({}, \'{}\', {}) RETURNING problem_id;'.format(
                bookid, page, no)
            self.writeLog("ADMIN", query)
            cur.execute(query)
            pid = cur.fetchall()[0][0]

            return [False, pid]
        except Exception as ex:
            return [True, str(ex)]

    def updateQuestionMessage(self, qid, msg, nick, ip):
        cur = self.getCursor()

        try:
            query = 'UPDATE question SET message = \'{}\' WHERE question_id = \'{}\';'.format(msg, qid)
            self.writeLog("ADMIN", query)
            cur.execute(query)

            self._send_webhook("질문 문구수정", "QuestionID: {}\nNewMessage:{}\n\n관리자에 의해 질문의 상태메세지가 수정되었습니다.".format(qid, msg),
                               "{}".format(nick), "DB.updateQuestionMessage", ip, colour=3092790)

            return [False, None]
        except Exception as ex:
            return [True, str(ex)]

    def markQuestion(self, qid, nick, ip):
        cur = self.getCursor()

        try:
            query = 'UPDATE question SET status=2 WHERE question_id = \'{}\';'.format(qid)
            self.writeLog("ADMIN", query)
            cur.execute(query)

            self._send_webhook("질문수정", "QuestionID: {}\n\n관리자에 의해 질문이 오류로 표기되었습니다.".format(qid),
                               "{}".format(nick), "DB.markQuestion", ip, colour=3092790)

            return [False, None]
        except Exception as ex:
            return [True, str(ex)]

    def deleteQuestion(self, qid, nick, ip):
        cur = self.getCursor()

        try:
            query = 'DELETE FROM question WHERE question_id=\'{}\';'.format(qid)
            self.writeLog("ADMIN", query)
            cur.execute(query)

            self._send_webhook("질문삭제", "QuestionID: {}\n\n관리자에 의해 질문이 삭제되었습니다.".format(qid),
                               "{}".format(nick), "DB.deleteQuestion", ip, colour=13369344)

            return [False, None]
        except Exception as ex:
            return [True, str(ex)]

    def deleteProblem(self, pid, nick, ip):
        cur = self.getCursor()

        try:
            query = 'DELETE FROM problem WHERE problem_id=\'{}\';'.format(pid)
            self.writeLog("ADMIN", query)
            cur.execute(query)

            self._send_webhook("문항삭제", "QuestionID: {}\n\n관리자에 의해 질문이 삭제되었습니다.".format(pid),
                               "{}".format(nick), "DB.deleteProblem", ip, colour=13369344)

            return [False, None]
        except Exception as ex:
            return [True, str(ex)]

    def deleteVideo(self, pid, nick, ip):
        cur = self.getCursor()

        try:
            query = 'DELETE FROM solution_video WHERE problem_id=\'{}\';'.format(pid)
            self.writeLog("ADMIN", query)
            cur.execute(query)

            self._send_webhook("영상삭제", "ProblemID: {}\n\n관리자에 의해 영상이 삭제되었습니다.".format(pid),
                               "{}".format(nick), "DB.deleteVideo", ip, colour=13369344)

            return [False, None]
        except Exception as ex:
            return [True, str(ex)]

    def run(self, query):
        cur = self.getCursor()
        cur.execute(query)
        return cur.fetchall()
