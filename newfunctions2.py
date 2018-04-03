# coding: utf-8
def cookSoup(url):
    url = urlNorm(url)
    i = 0
    while i<3:
        try:
            html = urlopen(url)
            code = html.read().decode(errors='ignore')
            bs = BeautifulSoup(code, "lxml")
            return bs
        except:
            print("Can't load ", url, sep='')
            i += 1
    raise Exception
