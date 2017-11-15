import htmls

class Settings:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 88

        self.html = htmls.Html()

        self.hostKey = "YOUR KEY HERE"

        self.rootDir = __import__("os").getcwd()
        self.htmlDir = self.rootDir+"/html/"
