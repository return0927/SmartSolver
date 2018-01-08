import psycopg2
import re
import validater
from datetime import datetime

class DB:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.user = "root"
        self.pw = "SmartSolve2017!@#"
        self.db = "ssolve"

        self.conn = None
        self.cursor = None
        self.logfile = "logs/db/%s.txt"

        self.getConn()

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
        if self.conn is None:
            self.getConn()

        if self.cursor is None:
            self.cursor = self.conn.cursor()

        return self.cursor

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
            self.writeLog("LOCAL", query)

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
            self.writeLog("LOCAL", query)

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
            self.writeLog("LOCAL", query)

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
            self.writeLog("LOCAL", query)
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
            self.writeLog("LOCAL", query)
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
            self.writeLog("LOCAL", query)
            cur.execute(query)
            result = cur.fetchall()
            if len(result): return [False, result[0][0]]
            else: return [False, False]
        except Exception as ex:
            raise ex
            print(ex)
            return [True, str(ex)]

    def submitmyQuestion(self, _requester, subj, bookseries, year, page, no, ip):
        cur = self.getCursor()

        try:
            err, bookid = self.getBook(subj, bookseries, year)
            if err: raise Exception(bookid)
            err, pid = self.getProblemId(book_id=bookid, page=page, number=no)
            if err: raise Exception(pid)
            if pid:
                print("Already Uploaded Question-Problem")
                query = 'INSERT INTO question (problem_id, student_id) VALUES ({}, \'{}\') RETURNING question_id;'.format(pid, _requester)
                self.writeLog(ip, query)
                cur.execute(query)
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
            if err: pass
            else:
                if data is False: pass
                else:
                    query = 'UPDATE question SET status = 1, message = \'자동답변\', p_time = current_date, p_time_ = now() WHERE question_id=\'{}\';'.format(qid)
                    self.writeLog("AUTOMATION", query)
                    cur.execute(query)

            return [False, "질문이 등록되었습니다."]
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
            query = 'SELECT rate_limit FROM users WHERE id=\'{}\';'.format(User['id'])
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0]]

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


    def run(self, query):
        cur = self.getCursor()
        cur.execute(query)
        return cur.fetchall()
