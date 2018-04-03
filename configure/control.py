import os

from flask import Flask, request, url_for, session, redirect, render_template

app = Flask(__name__)
path = os.getcwd()

@app.route('/')
def application():
    return render_template('index.html')

@app.route('/test.html')
def test():
    return render_template('test.html')

@app.route('/ajax_info.txt',  methods=['POST'])
def get_new_elem():
    f = open('ajax_info.txt').read()
    print(request.data)
    return f + ' pososi' + request.data.decode()

@app.route('/objects',  methods=['POST'])
def saveObject():
    if not bool(request.args):
        count = 1
        while "object"+str(count) in os.listdir("objects"):
            count += 1
        f = open("objects/object"+str(count), "x")
        print("opened!")
        f.write(request.data.decode())
        print("wrote!")
        return "OK"
    else:
        obj = request.args['del']
        os.remove("objects/"+obj)
        return "OK"


@app.route('/objects',  methods=['GET'])
def sendObjects():
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


@app.route('/index.html',  methods=['GET'])
def get_new_elem1():
    name = request.args['object']
    try:
        f = open("objects/" + name).read()
    except:
        return "Can't open file \'" + name + "\'"
    elems = f.split('|')
    res = "<b>URL:</b> "+elems[0]+"\n<b>Name:</b> "+elems[1]+"\n<b>Emails:</b>\n"
    for addr in elems[2].split('\n'):
        res = res + "  " + addr + '\n'
    res = res+"<b>Schedule:</b> "+elems[3]+"\n<b>History:</b> "+elems[4]
    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0')
