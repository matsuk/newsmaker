# coding: utf-8
class Newsmaker:
    def __init__(self, config):
        self.urlList = []
    def __repr__(self):
        return "meow"
    def addUrl(self, url, emails=None, schedule=None, historyLength=None, name=None):
        if type(url) == str:
            temp = Page(url, emails, schedule, historyLength, name)
        elif type(url) == Page:
            temp = url
        self.urlList.append(temp)
    def start(self):
        b
        
class Page:
    def __init__(self, url, emails=None, schedule=None, historyLength=5, name=url):
        self.url = url
        self.emails = emails
        self.schedule = schedule
        self.historyLength = historyLength
        self.name = name
    def __repr__(self):
        s = 'URL: '+self.url+'\n'
        s += 'E-mails:\n'
        if self.emails != None:
            for addr in self.emails:
                s += '  '+addr+'\n'
        s += 'Schedule: '+str(self.schedule)+'\n'
        s += 'History length: '+str(self.historyLength)+'\n'
        s += 'Name: '+self.name+'\n'
        return s
        
def checkNewsObj(page):
    if page != None and type(page) == Page:
        if page.url == page.name:
            name = (urllib.parse.urlparse(page.name).netloc+urllib.parse.urlparse(page.name).path).replace('.', '_').replace('/', '-').replace('\n', '')
        else:
            name = page.name
        if not os.path.exists(name):
            os.makedirs(name)
            print("Directory created: ", name, sep='')
        lst = os.listdir(name)
        lst.sort()
        now = datetime.datetime.now()
        now = now.year.__str__()+'-'+now.month.__str__()+'-'+now.day.__str__()+'-'+now.hour.__str__()+'-'+now.minute.__str__()+'-'+now.second.__str__()
        if len(lst) < page.historyLength:
            if len(lst) != 0:
                try:
                    checkPage(page.url, name+'/'+lst[len(lst)-1], name+'/'+now+'.html')
                except Exception as err:
                    print(err)
                    print("Can't check!")
            else:
                try:
                    checkPage(page.url, 'temp', name+'/'+now+'.html')
                except Exception as err:
                    print(err)
                    print("Can't check!")
        else:
            os.remove(name+'/'+lst[0])
            try:
                checkPage(page.url, name+'/'+lst[len(lst)-1]+'.html', name+'/'+now+'.html')
            except Exception as err:
                print(err)
                print("Can't check!")
        print("Page saved as ", name+now, sep='')
        
