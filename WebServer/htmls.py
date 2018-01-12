import codecs


class Html:
    def __init__(self):
        self.root = self.Loader("html/index.html")
        self.login = self.Loader("html/login.html")
        self.register = self.Loader("html/register.html")
        self.verify = self.Loader("html/verify.html")
        self.promotion = self.Loader("html/promotion.html")
        self.flowplayer = self.Loader("html/players/index.html")

        self.panel = self.Loader("html/panel.html")

        self.error = self.Loader("html/error.html")

    def Loader(self, path):
        return codecs.open(path, "r", encoding="UTF-8").read()