#!/usr/bin/env python
#coding:utf-8

from flask import Flask,request,render_template
import pixivSearch as pixiv
from StringIO import StringIO
app = Flask(__name__)
s=pixiv.getsession()

@app.route('/')
def index():
    urls=list()
    return render_template('search.html',urls=urls)

@app.route('/search')
def search():
    keyword=request.args.get('keyword').encode('utf8')
    number=int(request.args.get('number'))
    pages=pixiv.getpage(s,keyword,number)
    urls=pixiv.getlist(s,keyword,number,pages)
    return render_template('search.html',urls=urls)

@app.route('/imgthumb')
def imgthumb():
    url=request.args.get('url')
    r=s.get(url,headers={'referer':'http://www.pixiv.net/'},timeout=10)
    img = (StringIO(r.content))
    response = app.make_response(img.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

if __name__=='__main__':
    app.run(port=3000,debug=True)