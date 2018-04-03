import urllib.parse
import os
import re
import requests
import copy
from urllib.request import urlopen
from readability import Document
from bs4 import BeautifulSoup
import urllib
import difflib
import datetime

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

def diffA(text1, text2):
    text = ''
    d = difflib.Differ()
    result = list(d.compare(text1, text2))
    i = 0
    line = ''
    sign = ' '
    for char in result:
        if sign == ' ':
            if char[0] == ' ':
                text += char[2]
            elif char[0] == '+':
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker1\">"
                text += char[2]
                sign = '+'
            elif char[0] == '-':
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
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker1\">"
                text += char[2]
                sign = '+'
            elif char[0] == '-':
                text += char[2]
    return text
def savetag(tag, name='tag', overwrite=False):
    if overwrite == False:
        num = 0
        while name+num.__str__()+'.html' in os.listdir():
            num += 1
        file = open(name+num.__str__()+'.html', "w")
        file.write(tag.__str__())
    else:
        file = open(name, "w")
        file.write(tag.__str__())
    
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
        for tag in bs2.findAll("span", attrs={'class':'newsmaker1'}):
            tag.replaceWithChildren()
        for tag in bs2.findAll("span", attrs={'class':'newsmaker2'}):
            tag.replaceWith('')
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
    return url

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
        print('Success!')
        bs = BeautifulSoup(code, "lxml")
        return bs
    print("Can't load page "+url)
    return None

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
    def __init__(self, url, emails=None, schedule=None, historyLength=5, name=None):
        self.url = url
        self.emails = emails
        self.schedule = schedule
        self.historyLength = historyLength
        if name != None:
            self.name = name
        else:
            self.name = url
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
        
