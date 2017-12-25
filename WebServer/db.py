import psycopg2
import re
import validater
from datetime import datetime

class DB:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.user = "ssolve"
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

        query = 'SELECT "id" FROM "User" WHERE id=\'%s\'' % id
        self.writeLog(_ip, query)

        cur.execute(query)

        _data = cur.fetchall()
        return _data

    def checkEmailExist(self, email, _ip):
        err, _ = validater.email(email)
        if err: return True

        cur = self.getCursor()

        query = 'SELECT "email" FROM "User" WHERE email=\'%s\'' % email
        self.writeLog(_ip, query)

        cur.execute(query)
        _data = cur.fetchall()
        return _data

    def addUser(self, _id, _pw, _name, _bir, _gra, _email, _ip, _code):
        if not self.hardfilter(_id): return "Invalid Query"
        if validater.email(_email)[0]: return "Invalid Query"

        cur = self.getCursor()
        try:
            cur.execute('INSERT INTO "User" VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (
                _id, _pw, _name, _bir, _gra, _email, _ip, _ip, _code))
            self.conn.commit()
            return False
        except Exception as ex:
            return str(ex)

    def submitRecentIP(self, _id, _ip):
        cur = self.getCursor()
        try:
            query = 'UPDATE "User" SET recentip = \'%s\' WHERE id = \'%s\';'%(_ip, _id)
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
            query = 'SELECT "name", "email_veri" FROM "User" WHERE id=\'%s\' and pw=\'%s\''%(_id,_pw)
            self.writeLog(_ip, query)

            cur.execute(query)
            result = cur.fetchall()
            print(result)

            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getTextBooks(self, ip, selection="*", curr=None):
        cur = self.getCursor()

        try:
            if curr:
                query = 'SELECT %s FROM "tbooks" WHERE curriculumn = \'%s\';' % (selection, curr)
                self.writeLog(ip, query)

                cur.execute(query)
            else:
                query = 'SELECT %s FROM "tbook";' % (selection)
                self.writeLog(ip, query)

                cur.execute(query)
            result = cur.fetchall()
            return [False, sorted(result)]
        except Exception as ex:
            return [True, str(ex)]

    def getCurriculumn(self, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT DISTINCT curriculumn FROM "tbooks";'
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getBookModifiedYear(self, curr, book, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT year_modified FROM "tbooks" WHERE curriculumn=\'%s\' and bookname = \'%s\';'%(curr,book)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getBookPublisher(self, curr, book, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT publisher FROM "tbooks" WHERE curriculumn=\'%s\' and bookname = \'%s\';'%(curr,book)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0]]
        except Exception as ex:
            return [True, str(ex)]

    def getBookNotice(self, curr, book, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT notice FROM "tbooks" WHERE curriculumn=\'%s\' and bookname = \'%s\';'%(curr,book)
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, result[0]]
        except Exception as ex:
            return [True, str(ex)]

    # --- Promotion ---
    def getPromotionVid(self, ip):
        cur = self.getCursor()

        try:
            query = "SELECT curr, book, year, page, num, vid FROM video WHERE published=1";
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, sorted(result, key=lambda x: x[5])]
        except Exception as ex:
            return [True, str(ex)]

    # --- MyPage ---
    def getMyQuestion(self, User, ip):
        cur = self.getCursor()

        try:
            query = 'SELECT timestamp, qnum, status, content, link, tbook_id, number FROM questions WHERE requester=\'{}\''.format(User['id'])
            self.writeLog(ip, query)

            cur.execute(query)
            result = cur.fetchall()
            return [False, sorted(result, key=lambda x: x[1])]

        except Exception as ex:
            print(ex)
            return [True, str(ex)]

    def run(self, query):
        cur = self.getCursor()
        cur.execute(query)
        return cur.fetchall()