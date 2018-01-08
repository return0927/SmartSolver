import htmls

class Settings:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 80

        self.html = htmls.Html()

        self.hostKey = "Onpool.kr-2018-R3turnDev-Leh852901-2017!@#"

        self.rootDir = __import__("os").getcwd()
        self.htmlDir = self.rootDir+"/html/"

        self.admins = ["bc1916", "sunsky"]
