# coding: utf-8
def checkNews(config='config'):
    for line in open(config, 'r').readlines():
        name = (urllib.parse.urlparse(line).netloc+urllib.parse.urlparse(line).path).replace('.', '_').replace('/', '-').replace('\n', '')
        if not os.path.exists(name):
            os.makedirs(name)
            print("Directory created: ", name, sep='')
        lst = os.listdir(name)
        lst.sort()
        now = datetime.datetime.now()
        now = now.year.__str__()+'-'+now.month.__str__()+'-'+now.day.__str__()+'-'+now.hour.__str__()+'-'+now.minute.__str__()+'-'+now.second.__str__()
        if len(lst) < 5:
            if len(lst) != 0:
                try:
                    checkPage(line, name+'/'+lst[len(lst)-1], name+'/'+now+'.html')
                except Exception as err:
                    print(err)
                    print("Can't check!")
                    continue
            else:
                try:
                    checkPage(line, 'temp', name+'/'+now+'.html')
                except Exception as err:
                    print(err)
                    print("Can't check!")
                    continue
        else:
            os.remove(name+'/'+lst[0])
            try:
                checkPage(line, name+'/'+lst[len(lst)-1]+'.html', name+'/'+now+'.html')
            except Exception as err:
                print(err)
                print("Can't check!")
                continue
        print("Page saved as ", name+now, sep='')
        
def findText(bs):
    par = set()
    l = []
    for tag in bs.findAll({'p', 'br', 'hr', re.compile("h[1-6]")}):
        par.add(tag.parent)
    for tag in par:
        br = len(tag.findChildren("br", recursive=False))
        p = len(tag.findChildren("p",  recursive=False))
        hr = len(tag.findChildren("hr", recursive=False))
        hs = len(tag.findChildren(re.compile("h[1-6]"), recursive=False))
        l.append((tag, br+p+hr+hs))
        #print(tag.name, br, p, hr, hs)
    max = 0
    _i = 0
    for i in range(len(l)):
        if l[i][1] > max:
            max = l[i][1]
            _i = i
    return l[_i][0]
def checkPage(url, prev="prev.html", new="prev.html"):
    bs1 = cookSoup(url)
    print("prev = ", prev, sep='')
    print("new = ", new, sep='')
    print(os.path.isfile(prev))
    if os.path.isfile(prev):
        bs2 = BeautifulSoup(open(prev, "r").read(), "lxml")
        for tag in bs2.findAll("span", attrs={'class':'newsmaker'}):
            tag.replaceWithChildren()
        tag1 = findText(bs1)
        tag2 = findText(bs2)
        text1 = tag1.__str__()
        text2 = tag2.__str__()
        text = diffA(text2, text1)
        newtag = BeautifulSoup(text, "lxml")
        newtag = newtag.contents[0].contents[0].contents[0]
        findText(bs1).replaceWith(newtag)
    savetag(bs1, new, True)
def urlNorm(url):
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    print(url)
    return url
def cookSoup(url):
    url = urlNorm(url)
    i = 0
    while i<3:
        try:
            html = urlopen(url)
            code = html.read().decode()
            bs = BeautifulSoup(code, "lxml")
            return bs
        except:
            print("Can't load ", url, sep='')
            i += 1
    raise Exception
