import codecs


class Html:
    def __init__(self):
        self.root = self.Loader("html/index.html")
        self.login = self.Loader("html/login.html")
        self.register = self.Loader("html/register.html")

    def Loader(self, path):
        return codecs.open(path, "r", encoding="UTF-8").read()