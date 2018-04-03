# coding: utf-8
def cookSoup(url):
    url = urlNorm(url)
    i = 0
    while i<3:
        try:
            html = urlopen(url)
        except Exception as err:
            print(err)
            i += 1
            continue
        code = html.read()
        try:
            code = code.decode(encoding='utf-8')
        except UnicodeDecodeError as err:
            print(err)
            print('Trying \'cp1251\'...', sep='')
            try:
                code = code.decode(encoding='cp1251')
            except:
                print(err)
                return None
        print('Success!')
        bs = BeautifulSoup(code, "lxml")
        return bs
    print("Can't load page "+url)
    return None
