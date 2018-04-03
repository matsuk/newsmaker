# coding: utf-8
def checkPage(url, prev="prev.html"):
    bs1 = cookSoup(url)
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
    savetag(bs1, "prev.html", True)
    
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
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker\">"
                text += char[2]
                sign = '+'
            elif char[0] == '-':
                text += "<span style=\"background-color: #EBA2A9\" title=\"Deleted text\" class=\"newsmaker\">"
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
                text += "<span style=\"background-color: #EBA2A9\" title=\"Deleted text\" class=\"newsmaker\">"
                text += char[2]
                sign = '-'
        elif sign == '-':
            if char[0] == ' ':
                text += "</span>"
                text += char[2]
                sign = ' '
            elif char[0] == '+':
                text += "</span>"
                text += "<span style=\"background-color: #B4EBA2\" title=\"Added text\" class=\"newsmaker\">"
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
            
