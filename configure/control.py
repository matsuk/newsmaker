import os

from flask import Flask, request, url_for, session, redirect, render_template

app = Flask(__name__)
path = os.getcwd()

@app.route('/')
def application():
    return render_template('index.html')

@app.route('/append', methods=['POST'])
def appendGroup():
    name = request.args['append']
    print("I'm working!")
    print(request.data.decode())
    try:
        f = open("groups/" + name, 'a').write(request.data.decode()+',')
    except:
        return "Can't open file \'" + name + "\'"
    return "OK"

@app.route('/objects',  methods=['POST'])
def saveObject():
    if 'append' in request.args.keys():
        count = 1
        if not os.path.isdir('objects'):
            os.makedirs('objects')
        while "object"+str(count) in os.listdir("objects"):
            count += 1
        name = 'object'+str(count)
        try:
            f = open("objects/"+name, "x")
        except:
            return "Can't open file \'" + name + "\'"
        f.write(request.data.decode())

        group = request.args['append']
        try:
            f = open("groups/" + group, 'a').write(name+',')
        except:
            return "Can't open file \'" + group + "\'"
        return name
    elif 'del' in request.args.keys():
        obj = request.args['del']
        group = request.args['mod']
        os.remove("objects/"+obj)
        try:
            f = open("groups/"+group)
        except:
            return "Can't open file \'" + group + "\'"
        temp = f.read()
        print("temp=",temp)
        l = temp.split('|')[2].split(',')
        substr = temp.split('|')
        substr = substr[0]+'|'+substr[1]
        l.remove(obj)
        substr += '|'
        substr += ','.join(l)
        print("sub=",substr)
        try:
            f = open("groups/"+group, "w").write(substr)
        except:
            return "Can't open file \'" + group + "\'"
        return "OK"


@app.route('/objects',  methods=['GET'])
def sendObjects():
    if not request.args:
        objs = os.listdir('objects')
        objs = [x for x in objs if x.startswith('object')]
        num = len(objs)
        s = str(num) + ','
        for name in objs:
            print(name)
            f = open("objects/"+name, 'r').read()
            elems = f.split('|')
            s = s + elems[1] + ':' + name + ','
        print(s)
        return s
    elif 'objs' in request.args.keys():
        name = request.args['objs']
        try:
            f = open("groups/" + name).read()
        except:
            return "Can't open file \'" + name + "\'"
        objs = f.split('|')[2].split(',')[:-1]
        #objs = ['object'+str(x) for x in nums]
        num = len(objs)
        s = str(num) + ','
        for name in objs:
            print(name)
            f = open("objects/"+name, 'r').read()
            elems = f.split('|')
            s = s + elems[1] + ':' + name + ','
        print(s)
        return s

@app.route('/groups',  methods=['POST'])
def saveGroup():
    if not bool(request.args):
        count = 1
        if not os.path.isdir('groups'):
            os.makedirs('groups')
        while "group"+str(count) in os.listdir("groups"):
            count += 1
        f = open("groups/group"+str(count), "x")
        print("opened!")
        f.write(request.data.decode())
        print("wrote!")
        return "OK"
    else:
        obj = request.args['del']
        os.remove("groups/"+obj)
        return "OK"

@app.route('/groups',  methods=['GET'])
def sendGroups():
    if not request.args:
        objs = os.listdir('groups')
        objs = [x for x in objs if x.startswith('group')]
        num = len(objs)
        s = str(num) + ','
        for name in objs:
            print(name)
            f = open("groups/"+name, 'r').read()
            elems = f.split('|')
            s = s + elems[0] + ':' + name + ','
        print(s)
        return s
    elif 'del' in request.args.keys():
        obj = request.args('del')
        os.remove('groups/'+obj)
        return "OK"


@app.route('/index.html',  methods=['GET'])
def get_new_elem_1():
    if 'object' in request.args.keys():
        name = request.args['object']
        try:
            f = open("objects/" + name).read()
        except:
            return "Can't open file \'" + name + "\'"
        elems = f.split('|')
        res = "<b>URL:</b> "+elems[0]+"\n<b>Name:</b> "+elems[1]
        res = res+"\n<b>History:</b> "+elems[2]
        return res
    elif 'group' in request.args.keys():
        name = request.args['group']
        try:
            f = open("groups/" + name).read()
        except:
            return "Can't open file \'" + name + "\'"
        elems = f.split('|')
        res = "<b>Name:</b> "+elems[0]+"\n<b>Emails:</b>\n"
        for addr in elems[1].split('\n'):
            res = res + "  " + addr + '\n'
        res = res + '|' + elems[2] + '\n'
        return res

if __name__ == '__main__':
    app.run(host='0.0.0.0')
