import urllib.parse
import os
import re
import requests
import copy
from urllib.request import urlopen
from readability import Document
from bs4 import BeautifulSoup
import urllib

def checkLines(l1, l2):
    """Rubbish"""
    if len(l1) == len(l2):
        errors = []
        for i in range(l1):
            if l1[i] != l2[i]:
                errors.append((i, l1[i], l2[i]))
        if errors == []:
            print("Equal!")
        else:
            for err in errors:
                print("Line ", err[0], ":\nWas: ", err[1], "\nNow: ", err[2], sep='')
    if len(l2) > len(l1):
        errors = []
        for i in range(l1):
            if l1[i] not in l2:
                asd
                
                
def compareStr(str1, str2):
    list1 = str1.splitlines()
    list2 = str2.splitlines()
    count = 0
    for i in range(min(len(list1), len(list2))):
        if list1[i] != list2[i]:
            print("line ", i, ":\n    ", list1[i], "\n    ", list2[i], sep='')
            count += 1
    print(count, "discrepancies")
    
def cookSoup(url):
    """Make a BeautifulSoup object from any url (kirillic allowed)"""
    url = urlNorm(url)
    html = urlopen(url)
    code = html.read().decode()
    bs = BeautifulSoup(code, "lxml")
    return bs

def delSpaces(list):
    buf = 'a'
    for i in range(len(list)):
        buf1 = list[i]
        if list[i] == buf and list[i] == '':
            del list[i]
        buf = buf1
    return list

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
        
def savehtml(html, name='page'):
    num = 0
    while name+str(num)+'.html' in os.listdir():
        num += 1
    file = open(name+str(num)+'.html', "w")
    file.write(code)
        
def savetag(tag, name='tag'):
    num = 0
    while name+num.__str__()+'.html' in os.listdir():
        num += 1
    file = open(name+num.__str__()+'.html', "w")
    file.write(tag.__str__())
        
def tagToLines(tag, textOnly=True):
    if textOnly == True:
        s = tag.get_text().__str__()
        s = s.splitlines()
        s = delSpaces(s)
    else:
        s = tag.__str__()
        s = s.splitlines()
    return s
    
def urlNorm(url):
    url = urllib.parse.urlsplit(url)
    print(url)
    print(type(url))
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    print(url)
    return url
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
            
def addURL(url):
    bs = cookSoup(url)
    text = findText(bs)
    
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
        print(tag.name, br, p, hr, hs)
    max = 0
    _i = 0
    for i in range(len(l)):
        if l[i][1] > max:
            max = l[i][1]
            _i = i
    print(l[_i][0], ":", l[_i][1])
    return l[_i][0]

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
    
