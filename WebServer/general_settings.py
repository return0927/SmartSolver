import htmls

class Settings:
    def __init__(self):
        #Web
        self.webhost = "0.0.0.0"
        self.webport = 80

        self.html = htmls.Html()

        self.hostKey = "Onpool.kr-2018-R3turnDev-Leh852901-2017!@#"

        self.rootDir = __import__("os").getcwd()
        self.htmlDir = self.rootDir+"/html/"

        self.admins = ["bc1916", "sunsky"]

        # UX
        self.question_cost = 100

        # DB
        self.host = "localhost"
        self.port = 5432
        self.user = "root"
        self.pw = "SmartSolve2017!@#"
        self.db = "ssolve"