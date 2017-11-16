import psycopg2


class DB:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.user = "ssolve"
        self.pw = "SmartSolve2017!@#"
        self.db = "ssolve"

        self.conn = None
        self.cursor = None

        self.getConn()

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

    def getCursor(self):
        if self.conn is None:
            self.getConn()

        if self.cursor is None:
            self.cursor = self.conn.cursor()

        return self.cursor

    def checkIDExist(self, id):
        cur = self.getCursor()
        cur.execute('SELECT "id" FROM "User" WHERE id=\'%s\'' % id)
        _data = cur.fetchall()
        return _data

    def checkEmailExist(self, id):
        cur = self.getCursor()
        cur.execute('SELECT "email" FROM "User" WHERE email=\'%s\'' % id)
        _data = cur.fetchall()
        return _data

    def addUser(self, _id, _pw, _name, _bir, _gra, _email, _ip):
        cur = self.getCursor()
        try:
            cur.execute('INSERT INTO "User" VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\''')' % (
                _id, _pw, _name, _bir, _gra, _email, _ip, _ip))
            self.conn.commit()
            return False
        except Exception as ex:
            return str(ex)


    def getAccount(self, _id, _pw):
        cur = self.getCursor()
        try:
            cur.execute('SELECT "name" FROM "User" WHERE id=\'%s\' and pw=\'%s\''%(_id,_pw))
            result = cur.fetchall()
            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getTextBooks(self, selection="*", curr=None):
        cur = self.getCursor()

        try:
            if curr:
                cur.execute('SELECT %s FROM "tbooks" WHERE curriculumn = \'%s\';' % (selection, curr))
            else:
                cur.execute('SELECT %s FROM "tbook";' % (selection))
            result = cur.fetchall()
            return [False, sorted(result)]
        except Exception as ex:
            return [True, str(ex)]

    def getCurriculumn(self):
        cur = self.getCursor()

        try:
            cur.execute('SELECT DISTINCT curriculumn FROM "tbooks";')
            result = cur.fetchall()
            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getBookModifiedYear(self, curr, book):
        cur = self.getCursor()

        try:
            cur.execute('SELECT year_modified FROM "tbooks" WHERE curriculumn=\'%s\' and bookname = \'%s\';'%(curr,book))
            result = cur.fetchall()
            return [False, result]
        except Exception as ex:
            return [True, str(ex)]

    def getBookPublisher(self, curr, book):
        cur = self.getCursor()

        try:
            cur.execute('SELECT publisher FROM "tbooks" WHERE curriculumn=\'%s\' and bookname = \'%s\';'%(curr,book))
            result = cur.fetchall()
            return [False, result[0]]
        except Exception as ex:
            return [True, str(ex)]

    def getBookNotice(self, curr, book):
        cur = self.getCursor()

        try:
            cur.execute('SELECT notice FROM "tbooks" WHERE curriculumn=\'%s\' and bookname = \'%s\';'%(curr,book))
            result = cur.fetchall()
            return [False, result[0]]
        except Exception as ex:
            return [True, str(ex)]