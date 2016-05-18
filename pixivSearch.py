#!/usr/bin/python
# coding:utf-8

import requests
import threading
import math
import Queue
from bs4 import BeautifulSoup

class geturl(threading.Thread):
    def __init__(self,name,keyword,number,workqueue,urls,s):
        threading.Thread.__init__(self)
        self.name=name
        self.keyword=keyword
        self.number=number
        self.workqueue=workqueue
        self.urls=urls
        self.s=s
    def run(self):
        lock = threading.Lock()
        while not self.workqueue.empty():
            lock.acquire()
            item=self.workqueue.get()
            lock.release()
            try:
                html = self.s.get('http://www.pixiv.net/search.php?word='+self.keyword+'&p='+str(item),timeout=100)
                soup = BeautifulSoup(html.text,"html.parser")    
                for li in soup.find_all('li',class_='image-item'):
                    bookmark_a = li.find_all('a',class_='bookmark-count _ui-tooltip')
                    if len(bookmark_a):
                        num = int(bookmark_a[0].get_text())
                        if num>=self.number:
                            lock.acquire()
                            self.urls.append([li.find_all('img',class_='_thumbnail')[0]['src'],'http://www.pixiv.net'+li.a['href']])
                            lock.release()
            except BaseException,e:
                print 'page'+str(item)+'出错'
                lock.acquire()
                self.workqueue.put(item)
                lock.release()
                
def getlist(s,keyword,number,pages):
    workqueue = Queue.Queue()
    threadnum = 10
    threads = list()
    urls = list()

    for task in range(1,pages+1):
        workqueue.put(task)

    for i in range(threadnum):
        thread_name = 'thread%s' %i
        thread = geturl(thread_name,keyword,number,workqueue,urls,s)
        thread.start()
        threads.append(thread)
        
    for i in threads:
        i.join()
    return urls

def getpage(s,keyword,number):
    print '标签为 '+keyword+' 收藏数大于等于 '+str(number)+' 的链接'
    html = s.get('http://www.pixiv.net/search.php?word='+keyword)
    soup = BeautifulSoup(html.text,"html.parser")
    pages = (soup.find_all('span',class_='count-badge')[0].get_text())[0:-1]
    pages = int(math.ceil(float(pages)/20))
    print '总页数为 '+str(pages)
    return pages
    
def getsession():
    #登录pixiv
    s = requests.Session()
    payload = {'mode':'login','return_to':'/','pixiv_id':'你的账号','pass':'你的密码','skip':'1'}
    s.post('https://www.pixiv.net/login.php',data=payload)
    print '获取session'
    return s
    
if __name__=='__main__':
    keyword='和叶'
    number=1
    s=getsession()
    pages=getpage(s,keyword,number)
    urls=getlist(s,keyword,number,pages)
    print str(urls)