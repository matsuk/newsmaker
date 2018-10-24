import urllib.parse
import os
import re
import requests
import copy
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import urllib
import difflib
import smtplib
from smtplib import SMTPHeloError, SMTPAuthenticationError, SMTPException
import getpass
import base64
import time
import sys
from datetime import timedelta, datetime


def sortDate(x):
    """
    Key for sorting dates represented as strings.
    """
    date = x.split('.')[0].split('-')
    if len(date[1]) == 1:
        date[1] = '0' + date[1][0]
    if len(date[2]) == 1:
        date[2] = '0' + date[2][0]
    if len(date[3]) == 1:
        date[3] = '0' + date[3][0]
    if len(date[4]) == 1:
        date[4] = '0' + date[4][0]
    if len(date[5]) == 1:
        date[5] = '0' + date[5][0]
    return int(''.join(date))

def checkEqual(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

def texts(bs):
    return list(filter(lambda x: len(''.join(list(filter(lambda x2: x2.__class__.__name__ == 'NavigableString', 
                                                         x.contents)))) > 80, bs.findAll(['p', 'div'])))
def textSize(tag):
    return len(''.join(list(filter(lambda x2: x2.__class__.__name__ == 'NavigableString', tag.contents))))

def most_common(lst):
    return max(lst, key=lst.count)

def getSize(filename):
    f = open(filename)
    f.seek(0, 2)
    size = f.tell()
    return size

def preprocessText(text):
    words = []
    word = ''
    label = 'n'
    for c in text:
        if label == 'n':
            if word != '':
                words.append(word)
                word = ''
            if c == '<':
                label = 't'
                word += c
            elif c == ' ':
                words.append(c)
                word = ''
            else:
                label = 'w'
                word += c
        elif label == 't':  
            if c != '>':
                word += c
            else:
                label = 'n'
                word += c
        elif label == 'w':
            if c == '<':
                words.append(word)
                word = ''
                label = 't'
                word += c
            elif c == ' ':
                label = 'n'
                word += c
            else:
                word += c
    if word != '':
        words.append(word)
    return words

def getDiff(text1, text2):
    """
    Returns HTML with highlighted differnces between text1 and text2,
    also provides amount of added/removed elements.
    """
    text1 = preprocessText(text1)
    text2 = preprocessText(text2)
    text = ''
    d = difflib.Differ()
    result  = list(difflib.ndiff(text1, text2))
    i = 0
    line = ''
    sign = ' '
    rem = 0
    add = 0
    for char in result:
        if sign == ' ':
            if char[0] == ' ':
                text += char[2:]
            elif char[0] == '+':
                add += 1
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker1\">"
                text += char[2:]
                sign = '+'
            elif char[0] == '-':
                rem += 1
                text += "<span style=\"background-color: #EBA2A9\" title=\"Deleted text\" class=\"newsmaker2\">"
                text += char[2:]
                sign = '-'
        elif sign == '+':
            if char[0] == ' ':
                text += "</span>"
                text += char[2:]
                sign = ' '
            elif char[0] == '+':
                text += char[2:]
            elif char[0] == '-':
                text += "</span>"
                rem += 1
                text += "<span style=\"background-color: #EBA2A9\" title=\"Deleted text\" class=\"newsmaker2\">"
                text += char[2:]
                sign = '-'
        elif sign == '-':
            if char[0] == ' ':
                text += "</span>"
                text += char[2:]
                sign = ' '
            elif char[0] == '+':
                text += "</span>"
                add += 1
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker1\">"
                text += char[2:]
                sign = '+'
            elif char[0] == '-':
                text += char[2:]
    return text, (rem, add)


def saveTag(tag, name='tag', overwrite=False):
    """
    Saves BeautifulSoup tag as <name><num>.html if <overwrite> is False
    and <name>.html if <overwrite> is True.
    """
    if overwrite == False:
        num = 0
        while name+num.__str__()+'.html' in os.listdir():
            num += 1
        file = open(name+num.__str__()+'.html', "w")
        file.write(tag.__str__().replace('\r', '\n'))
    else:
        file = open(name, "w")
        file.write(tag.__str__().replace('\r', '\n'))
    
def findText(bs):
    """
    Simple text searcher, based on looking for headers, newline tags and paragraph tags.
    """
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
    max = 0
    _i = 0
    for i in range(len(l)):
        if l[i][1] > max:
            max = l[i][1]
            _i = i
    return l[_i][0]

def findTextNew(bs, bg_texts=5, main_to_bg_ratio=3.5, brfs_to_junk_ratio = 2.5, get_class=False):
    """
    Heuristic text searcher, which provides text types.
        "briefs": for pages containing series of nearly same-sized blocks.
        "article": for pages with a specific tag, which contains much more text than any other.
        "article_with_comments": there is a major block and a set of minor blocks.
        "unsolved": couldn't decide which type the text belongs to.
        "notext": the page doesn't contain text blocks.
    """
    page_class = None
    articles = bs.findAll('article')
    if len(articles) > 1:
        page_class = 'briefs'
        pars = articles
        while (not checkEqual(pars)) and ('html' not in [x.name for x in pars]):
            pars = [x.parent for x in pars]
        if 'html' not in [x.name for x in pars]:
            text = pars[0]
        else:
            page_class = 'unsolved'
            text = max(articles, key=lambda x: len(getWords(x)))
    elif len(articles) == 1:
        text_areas = texts(bs)
        if len(text_areas) > bg_texts:
            page_class = 'article_with_comments'
        else:
            page_class = 'article'
        text = articles[0]
    else:
        text_areas = texts(bs)
        if len(text_areas) > 1:
            texts_by_len = sorted(text_areas, key=textSize, reverse=True)
            if (textSize(texts_by_len[0]) / textSize(texts_by_len[1])) > main_to_bg_ratio:
                page_class = 'article_with_comments'
                text = texts_by_len[0]
            else:
                page_class = 'briefs'
                briefs = list(filter(lambda x: x.attrs.keys() == most_common([x1.attrs.keys() for x1 in text_areas]), text_areas))
                size = len(briefs)
                cur_size = size
                pars = briefs
                while (not checkEqual(pars)) and ('html' not in [x.name for x in pars]) and (size / cur_size < brfs_to_junk_ratio):
                    prev = pars
                    pars = [x.parent for x in pars]
                    if not checkEqual([x.attrs.keys() for x in pars]):
                        for i in range(len(pars)):
                            if prev[i].attrs.keys() != pars[i].attrs.keys():
                                new_keys = pars[i].attrs.keys()
                                break
                        for i in range(len(pars)):
                            if prev[i].attrs.keys() == pars[i].attrs.keys():
                                if pars[i].parent.attrs.keys() == new_keys:
                                    pars[i] = pars[i].parent
                    pars = list(filter(lambda x: x.attrs.keys() == most_common([x1.attrs.keys() for x1 in pars]), pars))
                    cur_size = len(pars)
                if checkEqual(pars):
                    text = pars[0]
                elif ('html' in [x.name for x in pars]):
                    page_class = 'unsolved'
                    text = max(briefs, key=lambda x: len(getWords(x)))
        elif len(text_areas) == 1:
            page_class = 'article'
            text = text_areas[0]
        else:
            page_class = 'notext'
            text = None
    if get_class == True:
        return text, page_class
    return text

def checkPage(url, prev="prev.html", new="prev.html", spec=None, attrs=None):
    """                                                                            
    Downloads page by url, compares it with 'prev' and 
    saves page with highlighted differences as 'new'.
    If 'prev' doesn't exist, just saves page to 'new'.
    """
    searcher = findTextNew
    rem = 0
    add = 0
    if spec == None and attrs != None:
        print('\'tag\' is None, but attrs is not: checking the whole page')
    bs1 = cookSoup(url)
    if os.path.isfile(prev):
        bs2 = BeautifulSoup(open(prev, "r").read(), "lxml")
        for tag in bs2.findAll("span", attrs={'class':'newsmaker1'}):
            tag.replaceWithChildren()
        for tag in bs2.findAll("span", attrs={'class':'newsmaker2'}):
            tag.replaceWith('')
        if spec == None:
            tag1, page_class = searcher(bs1, get_class=True)
            print(page_class)
            tag2 = searcher(bs2)
        elif spec != None:
            if attrs != None:
                tag1 = bs1.find(spec, attrs)
                tag2 = bs2.find(spec, attrs)
            else:
                tag1 = bs1.find(spec, attrs)
                tag2 = bs2.find(spec, attrs)
        text1 = tag1.__str__().replace('\r', '\n')
        text2 = tag2.__str__().replace('\r', '\n')
        text, (rem, add) = getDiff(text2, text1)
        newtag = BeautifulSoup(text, "lxml")
        newtag = newtag.contents[0].contents[0].contents[0]
        searcher(bs1).replaceWith(newtag)
    saveTag(bs1, new, True)
    return rem, add

def urlNorm(url):
    """
    Fix encoding issues, appearing in URLs
    
    Parameters
    ----------
    url: string
        Input URL to normalize

    Returns
    -------
    out: string
        Normalized URL
    """
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    return url

def cookSoup(url):
    """
    Download HTML page and parse with BeatifulSoup

    Parameters
    ----------
    url: string
        Page URL

    Returns
    -------
    out: BeatifulSoup object
        Parsed HTML tree
    """
    url = urlNorm(url)
    i = 0
    while i<3:
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req)
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
            except UnicodeDecodeError as err:
                print(err)
                return None
        #print('Success!')
        bs = BeautifulSoup(code, "lxml")
        return bs
    print("Can't load page "+url)
    return None

class Newsmaker:
    """
    Newsmaker is a main class to download and store pages and compare their versions,
    also provides tool to send notifications to receivers specified via web interface.
    
    Constructor initializes sender e-mail info and groups of receivers with corresponding 
    lists of pages.

    Groups first should be created via web interface (./configure/control.py), e-mail and
    SMTP server should be placed in ./configure/mail file. If SMTP is not specified it
    will be taken as "smtp.<e-mail server>". 

    Methods
    -------
    __init__(config)
        Intializes all needed info from ./<config> directory and asks for password, which
        will be stored in ./<config>/<pswd_file> in base64 encoding for Newsmaker.store_pass days.

    start()
        Checks changes in provided pages and saves them as HTMLs with highlighted elements.

    checkSMTP()
        Check SMTP connection with provided e-mail and password.

    sendNotifications(group)
        Send e-mails with changes info to receivers.

    enterPass(pswd_file)
        Asks for password and stores it in pswd_file in base64 encoding.

    test()
        Saves HTML code of pages with highlighted main text.

    Example
    -------
    >>> newsmaker = Newsmaker()
    >>> newsmaker.store_pass = 5
    >>> newsmaker.start()

    """
    tryNum = 0
    store_pass = 3
    def checkSMTP(self):
        try:
            server = smtplib.SMTP_SSL(self.host, 465)
            server.ehlo(self.addr)
            server.login(self.addr, self.pswd)
            server.quit()
            return 0
        except SMTPHeloError as e:
            print("Server did not reply")
            return 1
        except SMTPAuthenticationError as e:
            print("Incorrect username/password combination")
            self.tryNum += 1
            return 2
        except SMTPException as e:
            print("Authentication failed")
            return 3
        except:
            print('Authentication failed')
            return 3

    def sendNotifications(self, group):
        subject = 'Отслеживание обновлений'
        body_text = 'Сводка:\n'
        for i in range(len(group.pages)):
            rem = group.pages[i].data[0]
            add = group.pages[i].data[1]
            if rem == None and add == None:
                continue
            body_text += str(i+1) + ') '
            body_text += group.pages[i].name + '\n'
            if add == 0 and rem == 0:
                body_text += 'Изменений нет\n'
            else:
                body_text += 'Новых элементов: ' + str(add) + '\n'
                body_text += 'Удалено элементов: ' + str(rem) + '\n'
                body_text += 'Посмотрите изменения по адресу: ' + group.pages[i].url + '\n'
            body_text += '\n'
        BODY = "\r\n".join((
            "From: {}".format("Newsmaker"),
            "To: %s" % ', '.join(group.emails),
            "Subject: %s" % subject ,
            "",
            body_text
        ))
        success = False
        try:
            server = smtplib.SMTP_SSL(self.host, 465)
            server.ehlo(self.addr)
            server.login(self.addr, self.pswd)
            success = True
        except SMTPHeloError as e:
            print('Server did not reply')
        except SMTPAuthenticationError as e:
            print('Incorrect username/password combination')
        except SMTPException as e:
            print('Authentication failed')
        except:
            print('Authentication failed')
        if success:
            try:
                server.sendmail(self.addr, group.emails, BODY.encode('utf-8'))
            except SMTPException as e:
                print('Error: unable to send email', e)
            finally:
                server.quit()

    def enterPass(self, pswd_file):
        self.pswd = getpass.getpass()
        encoded_pswd = base64.b64encode(self.pswd.encode())
        open(pswd_file, 'w+').write(encoded_pswd.decode())

    def __init__(self, config='configure'):
        dir_objs = os.path.join(config, 'objects')
        dir_grps = os.path.join(config, 'groups')
        grps = []
        for name in [x for x in os.listdir(dir_grps) if x.startswith('group')]:
            objs = []
            f = open(dir_grps+"/"+name, 'r').read()
            lst = f.split('|')
            for obj_name in [x for x in os.listdir(dir_objs) if x.startswith('object') and x in lst[2]]:
                obj_f = open(dir_objs+'/'+obj_name).read()
                lst1 = obj_f.split('|')
                obj = Page(lst1[0], lst1[1], int(lst1[2]))
                objs.append(obj)
            grp = Group(lst[0], lst[1].split('\n'), objs)
            grps.append(grp)
        self.grps = grps
        mail_info = open(os.path.join(config, 'mail')).read().split('\n')
        self.addr = mail_info[0]
        if len(mail_info) > 1:
            self.host = mail_info[1]
        else:
            # Try to use smtp server as smtp.<domain_name>
            self.host = 'smtp.' + self.addr.split('@')[1]
        pswd_file = os.path.join(config, 'pswd')
        if os.path.isfile(pswd_file) and getSize(pswd_file) > 0:
            pswd_mod = datetime.fromtimestamp(os.path.getmtime(filename=pswd_file))
            present = datetime.now()
            delta = timedelta(days=self.store_pass)
            if present - delta > pswd_mod:
                # Re-enter password if expired
                self.enterPass(pswd_file)
            else:
                self.pswd = base64.b64decode(open(pswd_file).read()).decode()
        else:
            self.enterPass(pswd_file)
        code = self.checkSMTP()
        while code == 2 and self.tryNum < 3:
            self.enterPass(pswd_file)
            code = self.checkSMTP()
        if self.tryNum == 3 or code != 0:
            sys.exit(0)

    def __repr__(self):
        return self.grps

    def start(self, name=None, group_name=None):
        if name == None or group_name == None:
            for gr in self.grps:
                for page in gr.pages:
                    print(page.url)
                    page.checkNews()
                if len(gr.emails) != 0:
                    self.sendNotifications(gr)
        else:
            for gr in self.grps:
                if gr.name == group_name:
                    for page in gr.pages:
                        if page.name == name:
                            trash = page.checkNews()
    def test(self):
        for gr in self.grps:
            for page in gr.pages:
                print(page.url)
                page.saveHighlightedText()
        
class Page:
    """
    Class to operate with single page.

    Methods
    -------
    __init__(url, name=None, historyLength=5)
        Creates page object for specified URL. If name is not provided the URL will be 
        used as the name.

    checkNews()
        Check news for the page according to stored history. If no history is found, the page 
        will be simply saved.

    """
    def __init__(self, url, name=None, historyLength=5, **kwargs):
        self.url = url
        self.historyLength = historyLength
        self.tag = kwargs.get('tag', None)
        self.attrs = kwargs.get('attrs', None)
        self.data = None
        if name != None:
            self.name = name
        else:
            self.name = url
    def __repr__(self):
        s = 'URL: '+self.url+'\n'
        s += 'Name: '+self.name+'\n'
        s += 'History length: '+str(self.historyLength)+'\n'
        return s

    def checkNews(self):
        rem = None
        add = None
        if self != None and self.__class__.__name__ == 'Page':
            if self.url == self.name:
                name = (urllib.parse.urlparse(self.name).netloc+urllib.parse.urlparse(self.name).path).replace('.', '_').replace('/', '-').replace('\n', '')
            else:
                name = self.name
            if not os.path.exists(name):
                os.makedirs(name)
                print("Directory created: ", name, sep='')
            lst = os.listdir(name)
            lst = [x for x in os.listdir(name) if x.endswith('html')]
            lst.sort(key=sortDate)
            now = datetime.now()
            now = now.year.__str__()+'-'+now.month.__str__()+'-'+now.day.__str__()+'-'+now.hour.__str__()+'-'+now.minute.__str__()+'-'+now.second.__str__()
            if len(lst) < self.historyLength:
                if len(lst) != 0:
                    rem, add = checkPage(self.url, name+'/'+lst[len(lst)-1], name+'/'+now+'.html', self.tag, self.attrs)
                else:
                    bs = cookSoup(self.url)
                    saveTag(bs, name+'/'+now+'.html', True)
            else:
                os.remove(name+'/'+lst[0])
                print("Old file "+name+'/'+lst[0]+" removed")
                rem, add = checkPage(self.url, name+'/'+lst[len(lst)-1]+'.html', name+'/'+now+'.html', self.tag, self.attrs)
            print("Page saved as ", name+'/'+now, sep='')
            if rem == 0 and add == 0:
                print("No changes!")
            elif rem == None and add == None:
                print("No history for page")
            else:
                print("Added: ",add," lines\nRemoved: ",rem," lines", sep='')
            self.data = (rem, add)
        else:
            print('invalid arg')

    def saveHighlightedText(self, name='taghl'):
        bs = cookSoup(self.url)
        searcher = findTextNew
        text = searcher(bs)
        if text != None:
            newtag = BeautifulSoup(text.__str__(), 'lxml').contents[0].contents[0].contents[0]
            span = bs.new_tag('div', **{'class':'newsmaker3', 'style':'background-color: #FFFD86'})
            span.append(newtag)
            text.replaceWith(span)
            saveTag(bs, name=name)
        else:
            print('No text was found')

class Group:
    """
    Group class. Stores lists of e-mails and pages for current group.

    Methods
    -------
    __init__(name, emails, pages)
        Constructor.
        name: string
            Name of the group.
        emails: list of strings
            Recipients' e-mail addresses
        pages: list of Page-objects
            List of pages to check.
    """
    def __init__(self, name, emails=[], pages=[]):
        self.name = name
        self.emails = emails
        if '' in emails:
            emails.remove('')
        self.pages = pages
    def __repr__(self):
        return self.name

def findDeepestTag(bs, tag=None, depth=0):
    if bs.name == tag or tag == None:
        max_depth = depth
    else:
        max_depth = -1
    for child in bs.children:
        if child.name != None:
            child_depth = findDeepestTag(child, tag, depth+1)
            if child_depth > max_depth:
                max_depth = child_depth
    return max_depth

def printTagTree(bs, s=''):
    for child in bs.children:
        if child.name != None:
            print(s+child.name)
            printTagTree(child, s+'|  ')

def getDeepestTags(bs, tag=None, depth=0, max_depth=0):
    tags = []
    if depth == 0:
        max_depth = maxTagDepth(bs, tag)
    if depth == max_depth and (tag == None or tag == bs.name):
        tags.append(bs)
    for child in bs.children:
        if child.name != None:
            tags.extend(getDeepestTags(child, tag, depth+1, max_depth))
    return tags

def maxDepth(bs, depth=0):
    count = 0
    max_depth = depth
    for child in bs.children:
        if child.name != None:
            count += 1
            child_depth = maxDepth(child, depth+1)
            if child_depth > max_depth:
                max_depth = child_depth
    return max_depth

def allTagsNum(bs):
    count = 0
    for child in bs.children:
        if child.name != None:
            count += 1
            count += allTagsNum(child)
    return count

def printDeepestTags(bs, tag=None, depth=0, max_depth=0):
    if depth == 0:
        max_depth = maxTagDepth(bs, tag)
    if depth == max_depth and (tag == None or tag == bs.name):
        print(bs)
    for child in bs.children:
        if child.name != None:
            printDeepestTags(child, tag, depth+1, max_depth)

def maxTagDepth(bs, tag=None, depth=0):
    if bs.name == tag or tag == None:
        max_depth = depth
    else:
        max_depth = -1
    for child in bs.children:
        if child.name != None:
            child_depth = maxTagDepth(child, tag, depth+1)
            if child_depth > max_depth:
                max_depth = child_depth
    return max_depth

def getParagraphs(bs):
    return list(filter(lambda x: x != '', re.sub('(\n| ( )+)+', '\n', '\n'.join(list(map(lambda x: x.getText(), [bs])))).split('\n')))

def getParagraphsInLinks(bs):
    return list(filter(lambda x: x != '', re.sub('(\n| ( )+)+', '\n', '\n'.join(list(map(lambda x: x.getText(), bs.findAll('a', {'href':True}))))).split('\n')))

def getWords(bs):
    return [x for y in [x.split(' ') for x in getParagraphs(bs)] for x in y]

def getWordsInLinks(bs):
    return [x for y in [x.split(' ') for x in getParagraphsInLinks(bs)] for x in y] 

if __name__ == "__main__":
    news = Newsmaker()
    news.start()
