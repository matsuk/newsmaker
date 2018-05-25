import urllib.parse
import os
import re
import requests
import copy
from urllib.request import urlopen, Request
from readability import Document
from bs4 import BeautifulSoup
import urllib
import difflib
import datetime
import smtplib
import getpass


def sortDate(x):
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

def texts_old(bs):
    return list(filter(lambda x: any([len(x1) > 80 for x1 in filter(lambda x2: x2.__class__.__name__ == 'NavigableString', 
                                                              x.contents)]), bs.findAll(['p', 'div'])))
def texts(bs):
    return list(filter(lambda x: len(''.join(list(filter(lambda x2: x2.__class__.__name__ == 'NavigableString', 
                                                              x.contents)))) > 80, bs.findAll(['p', 'div'])))
def textSize(tag):
    return len(''.join(list(filter(lambda x2: x2.__class__.__name__ == 'NavigableString', tag.contents))))

def most_common(lst):
    return max(lst, key=lst.count)

def urlNorm(url):
    url = urllib.parse.urlsplit(url)
    print(url)
    print(type(url))
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    print(url)
    return url               
                
def compareStr(str1, str2):
    list1 = str1.splitlines()
    list2 = str2.splitlines()
    count = 0
    for i in range(min(len(list1), len(list2))):
        if list1[i] != list2[i]:
            print("line ", i, ":\n    ", list1[i], "\n    ", list2[i], sep='')
            count += 1
    print(count, "discrepancies")
    
def delSpaces(list):
    buf = 'a'
    for i in range(len(list)):
        buf1 = list[i]
        if list[i] == buf and list[i] == '':
            del list[i]
        buf = buf1
    return list

def savehtml(html, name='page'):
    num = 0
    while name+str(num)+'.html' in os.listdir():
        num += 1
    file = open(name+str(num)+'.html', "w")
    file.write(code)


        
def tagToLines(tag, textOnly=True):
    if textOnly == True:
        s = tag.get_text().__str__()
        s = s.splitlines()
        s = delSpaces(s)
    else:
        s = tag.__str__()
        s = s.splitlines()
    return s
    
def walkChildren(node):
    for child in node.children:
        if child.name == None:
            continue
        try:
            print(child.name)
            if child.name != "br" and child.name != "p":
                tag = walkChildren(child)
                return child.name+"->"+tag
            else:
                return child.name
        except Exception:
            continue
        
# coding: utf-8
def saveTableCmp(table, table1, name="tables/table"):
    t = csv.reader(open('tables/table1.csv', 'r'))
    num = 0
    while os.path.basename(name)+num.__str__()+'.csv' in os.listdir('tables'):
        num += 1
    csvFile = open(name+num.__str__()+'.csv', 'w')
    writer = csv.writer(csvFile)
    try:
        rows = table.findAll("tr")
        for row in rows:
            csvRow = []
            for cell in row.findAll(['td', 'th']):
                if cell.img != None:
                    value = cell.img.attrs['src']
                else:
                    value = cell.get_text()
                if value.startswith('\n'):
                    value = value[1:]
                if value.endswith('\n'):
                    value = value[:len(value)-1]
                value = value.replace('\n', ' ')
                csvRow.append(value)
            writer.writerow(csvRow)
    finally:
        csvFile.close()
        
def saveTable(table, name="tables/table"):
    num = 0
    while os.path.basename(name)+num.__str__()+'.csv' in os.listdir('tables'):
        num += 1
    csvFile = open(name+num.__str__()+'.csv', 'w')
    writer = csv.writer(csvFile)
    try:
        rows = table.findAll("tr")
        for row in rows:
            csvRow = []
            for cell in row.findAll(['td', 'th']):
                if cell.img != None:
                    value = cell.img.attrs['src']
                else:
                    value = cell.get_text()
                if value.startswith('\n'):
                    value = value[1:]
                if value.endswith('\n'):
                    value = value[:len(value)-1]
                value = value.replace('\n', ' ')
                csvRow.append(value)
            writer.writerow(csvRow)
            print(csvRow)
    finally:
        csvFile.close()
        
def diff(text1, text2):
    d = difflib.Differ()
    result = list(d.compare(text1, text2))
    i = 0
    for line in result:
        i += 1
        if line[0] != ' ' and line[0] != '?':
            print(i,':', line)
            i -= 1
            
def isText(tag):
    l = set()    
    for child in tag.children:
        if child.name != None:
            l.add(child.name)
        try:
            for subchild in child.children:
                if subchild.name != None:
                    l.add(subchild.name)
        except:
            print("Tag has no children!")
    if (('br' in l) or ('hr' in l) or ('p' in l)) and (('h1' in l) or ('h2' in l) or ('h3' in l) or ('h4' in l) or ('h5' in l) or ('h6' in l)):
        print("Looks like a text:")
        print(tag.get_text())
        return True
    else:
        print("Probably not a text:")
        print(tag.get_text())
        return False

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

def diffB(text1, text2):
    text = ''
    brackets = []
    d = difflib.Differ()
    result = list(d.compare(text1, text2))
    i = 0
    line = ''
    sign = ' '
    rem = 0
    add = 0
    #print(len(list(filter(lambda x: x == '<', [x1[2] for x1 in result]))))
    #print(len(list(filter(lambda x: x == '>', [x1[2] for x1 in result]))))
    for char in result:
        if char[2] == '<':
            text += char[2]
            brackets.append('<')
            continue
        if char[2] == '>':
            text += char[2]
            if len(brackets) > 0:
                brackets.pop()
            continue
        if len(brackets) != 0:
            text += char[2]
            continue
        if sign == ' ':
            if char[0] == ' ':
                text += char[2]
            elif char[0] == '+':
                add += 1
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker1\">"
                text += char[2]
                sign = '+'
            elif char[0] == '-':
                rem += 1
                text += "<span style=\"background-color: #EBA2A9\" title=\"Deleted text\" class=\"newsmaker2\">"
                text += char[2]
                sign = '-'
        elif sign == '+':
            if char[0] == ' ':
                text += "</span>"
                text += char[2]
                sign = ' '
            elif char[0] == '+':
                text += char[2]
            elif char[0] == '-':
                text += "</span>"
                rem += 1
                text += "<span style=\"background-color: #EBA2A9\" title=\"Deleted text\" class=\"newsmaker2\">"
                text += char[2]
                sign = '-'
        elif sign == '-':
            if char[0] == ' ':
                text += "</span>"
                text += char[2]
                sign = ' '
            elif char[0] == '+':
                text += "</span>"
                add += 1
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker1\">"
                text += char[2]
                sign = '+'
            elif char[0] == '-':
                text += char[2]
    return text, (rem, add)

def diffA(text1, text2):
    text1 = preprocessText(text1)
    text2 = preprocessText(text2)
    text = ''
    d = difflib.Differ()
    #result = list(d.compare(text1, text2))
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


def savetag(tag, name='tag', overwrite=False):
    if overwrite == False:
        num = 0
        while name+num.__str__()+'.html' in os.listdir():
            num += 1
        file = open(name+num.__str__()+'.html', "w")
        file.write(tag.__str__().replace('\r', '\n'))
    else:
        file = open(name, "w")
        file.write(tag.__str__().replace('\r', '\n'))
    
def diffL(text1, text2):
    d = difflib.Differ()
    result = list(d.compare(text1, text2))
    i = 0
    for letter in result:
        i += 1
        if letter[0] != ' ' and letter[0] != '?':
            print(i,':', letter)
            i -= 1

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
    max = 0
    _i = 0
    for i in range(len(l)):
        if l[i][1] > max:
            max = l[i][1]
            _i = i
    return l[_i][0]

def findTextNew(bs, bg_texts=5, main_to_bg_ratio=3.5, brfs_to_junk_ratio = 2.5, get_class=False):
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
    bs1 = cookSoup1(url)
    #print("prev = ", prev, sep='')
    #print("new = ", new, sep='')
    #print(os.path.isfile(prev))
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
        text, (rem, add) = diffA(text2, text1)
        newtag = BeautifulSoup(text, "lxml")
        newtag = newtag.contents[0].contents[0].contents[0]
        searcher(bs1).replaceWith(newtag)
    savetag(bs1, new, True)
    return rem, add

def urlNorm(url):
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    return url

def cookSoup1(url):
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
            except UnicodeDecodeError as err:
                print(err)
                return None
        #print('Success!')
        bs = BeautifulSoup(code, "lxml")
        return bs
    print("Can't load page "+url)
    return None

def cookSoup1(url):
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
    def __init__(self, config='configure'):
        dir_objs = config+'/objects'
        dir_grps = config+'/groups'
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
        f1 = open(config+'/mail').read().split('\n')
        self.addr = f1[0]
        self.pswd = f1[1]
        self.host = f1[2]
    def __repr__(self):
        return "meow"
    def addUrl(self, url, emails=None, schedule=None, historyLength=None, name=None):
        if type(url) == str:
            temp = Page(url, emails, schedule, historyLength, name)
        elif type(url) == Page:
            temp = url
        self.urlList.append(temp)
    def start(self, name=None, group_name=None):
        if name == None or group_name == None:
            for gr in self.grps:
                for i in range(len(gr.pages)):
                    print(gr.pages[i].url)
                    gr.pages[i].data = checkNewsObj(gr.pages[i])
                if len(gr.emails) != 0:
                    sendNotifications(self.host, self.addr, gr, self.pswd)
        else:
            for gr in self.grps:
                if gr.name == group_name:
                    for page in gr.pages:
                        if page.name == name:
                            trash = checkNewsObj(page)
    def test(self):
        for gr in self.grps:
            for page in gr.pages:
                print(page.url)
                bs = cookSoup1(page.url)
                saveHighlightedText1(bs)
        
class Page:            
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

class Group:
    def __init__(self, name, emails=[], pages=[]):
        self.name = name
        self.emails = emails
        if '' in emails:
            emails.remove('')
        self.pages = pages
    def __repr__(self):
        return self.name
        
def checkNewsObj(page):
    rem = None
    add = None
    if page != None and page.__class__.__name__ == 'Page':
        if page.url == page.name:
            name = (urllib.parse.urlparse(page.name).netloc+urllib.parse.urlparse(page.name).path).replace('.', '_').replace('/', '-').replace('\n', '')
        else:
            name = page.name
        if not os.path.exists(name):
            os.makedirs(name)
            print("Directory created: ", name, sep='')
        lst = os.listdir(name)
        lst = [x for x in os.listdir(name) if x.endswith('html')]
        lst.sort(key=sortDate)
        now = datetime.datetime.now()
        now = now.year.__str__()+'-'+now.month.__str__()+'-'+now.day.__str__()+'-'+now.hour.__str__()+'-'+now.minute.__str__()+'-'+now.second.__str__()
        if len(lst) < page.historyLength:
            if len(lst) != 0:
                rem, add = checkPage(page.url, name+'/'+lst[len(lst)-1], name+'/'+now+'.html', page.tag, page.attrs)
            else:
                bs = cookSoup1(page.url)
                savetag(bs, name+'/'+now+'.html', True)
                #try:
                #    rem, add = checkPage(page.url, 'temp', name+'/'+now+'.html', page.tag, page.attrs)
                #except Exception as err:
                #    print(err)
                #    print("Can't check!")
                #    return None
        else:
            os.remove(name+'/'+lst[0])
            print("Old file "+name+'/'+lst[0]+" removed")
            rem, add = checkPage(page.url, name+'/'+lst[len(lst)-1]+'.html', name+'/'+now+'.html', page.tag, page.attrs)
        print("Page saved as ", name+'/'+now, sep='')
        if rem == 0 and add == 0:
            print("No changes!")
        elif rem == None and add == None:
            print("No history for page")
        else:
            print("Added: ",add," lines\nRemoved: ",rem," lines", sep='')
        return rem, add
    else:
        print('invalid arg')

def loadObjects(directory="configure/objects"):
    directory = os.path.normpath(directory)
    objs = []
    for name in [x for x in os.listdir(directory) if x.startswith('object')]:
        f = open(directory+"/"+name, 'r').read()
        lst = f.split('|')
        obj = Page(lst[0], lst[1], lst[2].split('\n'), lst[3], int(lst[4]))
        objs.append(obj)
    return objs

def saveHighlightedText(bs, name='taghl'):
    searcher = findTextNew
    text = searcher(bs)
    if text != None:
        newtag = BeautifulSoup(text.__str__(), 'lxml').contents[0].contents[0].contents[0]
        span = bs.new_tag('div', **{'class':'newsmaker3', 'style':'background-color: #FFFD86'})
        span.append(newtag)
        text.replaceWith(span)
        savetag(bs, name=name)
    else:
        print('No text was found')

def saveHighlightedText1(bs, name='taghl'):
    searcher = findTextNew
    text = searcher(bs)
    if text != None:
        for tag in text.findAll(['div', 'p', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.attrs['style']='background-color: #FFFD86'
        savetag(bs, name=name)
    else:
        print('No text was found')

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

def delScripts(tag):
    for child in tag.findChildren():
        if child.name == 'script':
            child.replaceWith('')
            continue
        elif bool(child.findChildren()):
            delScripts(child)

def send_email(host, subject, to_addr, from_addr, body_text):
    BODY = "\r\n".join((
        "From: %s" % from_addr,
        "To: %s" % to_addr,
        "Subject: %s" % subject ,
        "",
        body_text
    ))
 
    server = smtplib.SMTP_SSL(host, 465)
    server.ehlo(from_addr)
    server.login(from_addr,'1410Vfwer1997')
    server.sendmail(from_addr, [to_addr], BODY)
    server.quit()

def sendNotifications(host, from_addr, group, pswd):
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
        "From: %s" % from_addr,
        "To: %s" % ', '.join(group.emails),
        "Subject: %s" % subject ,
        "",
        body_text
    ))
    server = smtplib.SMTP_SSL(host, 465)
    server.ehlo(from_addr)
    server.login(from_addr, pswd)
    server.sendmail(from_addr, group.emails, BODY.encode('utf-8'))
    server.quit()

def saveHighlightedText(bs):
    searcher = findTextNew
    text = searcher(bs)
    newtag = BeautifulSoup(text.__str__(), 'lxml').contents[0].contents[0].contents[0]
    span = bs.new_tag('div', **{'class':'newsmaker3', 'style':'background-color: #FFFD86'})
    span.append(newtag)
    text.replaceWith(span)
    savetag(bs, name='taghl')


if __name__ == "__main__":
    news = Newsmaker()
    news.start()
