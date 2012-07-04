#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib, urllib2, re, os, cookielib
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import Tkinter as Tk
from tkFont import Font

class AlbumData:
    def __init__(self):
        self.name = ''
        self.needpwd = False
        self.url = ''
        self.needdownload = Tk.IntVar()
        self.needdownload.set(0)
        self.pwd = Tk.StringVar()

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
elements = []

def downPics(soup, username, albumcode, fid):
    pics = soup.findAll(attrs={'id' : re.compile("pic$")})
    for pic in pics:
        url = pic.a['href']
        idname = url.split('/')[2]

        url = 'http://photo.pchome.com.tw' + url
        purl = 'http://photo.pchome.com.tw/s08/a/v/' + username + '/book' + str(albumcode) + '/p' + idname +'.jpg'
        filename = ('%04d' % fid) + '.jpg'
        fid = fid + 1

        req = urllib2.Request(purl)
        req.add_header('Host', 'photo.pchome.com.tw')
        req.add_header('Referer', url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.34 Safari/536.11')

        f = opener.open(req)
        with open(filename, 'wb') as wf:
            wf.write(f.read())
        f.close()
    return fid

def parseAndDownPics(elem, username, pwd):
    url = 'http://photo.pchome.com.tw' + elem.url
    print url
    albumcodestr = elem.url.split('/')[2]
    albumcode = int(albumcodestr)

    f = None
    if elem.needpwd:
        body = {'pwd': pwd}
        f = opener.open(url, urllib.urlencode(body))
    else:
        f = opener.open(url)

    s = f.read()
    if re.compile('PwdSet').search(s) != None:
        print '%s password error' % elem.name.encode('gbk')
        return

    soup = BeautifulSoup(unicode(s,"big5"), convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    fullName = soup.findAll('a', { 'href': elem.url })[0]
    elem.name = fullName.text

    if os.path.isdir(elem.name): pass
    else: os.mkdir(elem.name)
    os.chdir(elem.name)

    pageElem = soup.findAll('tr', { 'class': 'photo-normal1' })[0]
    pagecount = len(pageElem.findAll('a'))

    fid = downPics(soup, username, albumcode, 0)

    for i in range(1, pagecount):
        newurl = 'http://photo.pchome.com.tw/%s/%s*%s' % (username, albumcodestr, str(i+1))
        f = opener.open(newurl)
        soup = BeautifulSoup(unicode(f.read(),"big5"), convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        fid = downPics(soup, username, albumcode, fid)

    os.chdir('..')

#username = 'avhc4691'
#pwd = '123'

def getAlbumList(username):
    url = 'http://photo.pchome.com.tw/' + username
    f = opener.open(url)

    soup = BeautifulSoup(unicode(f.read(),"big5"), convertEntities=BeautifulStoneSoup.HTML_ENTITIES)

    albs = soup.findAll(attrs={'id' : re.compile("alb$")})
    for elem in albs:
        a = AlbumData()
        a.url = elem.a['href']
        imgs = elem.findAll('img')
        for img in imgs:
            if img['title'] == u'密碼保護':
                a.needpwd = True
        name = elem.findAll('div', { 'class': 'name' })[0]
        a.name = name.text
        elements.append(a)

def downAlbum(username, pwd):
    if os.path.isdir(username): pass
    else: os.mkdir(username)
    os.chdir(username)

    for elem in elements:
        if elem.needdownload.get() == 1:
            passwd = elem.pwd.get()
            if passwd == '': passwd = pwd
            parseAndDownPics(elem, username, passwd)

    os.chdir('..')

def createAlbumEntry(root, elem):
    container = Tk.Frame(root)
    check = Tk.Checkbutton(container, variable=elem.needdownload)
    check.pack(side=Tk.LEFT)
    label = Tk.Label(container, text=elem.name, anchor='w', font=ft, width=50)
    label.pack(side=Tk.LEFT)
    text = Tk.Entry(container, textvariable=elem.pwd, font= ft)
    text.pack(side=Tk.RIGHT)
    container.pack(side=Tk.TOP)

#主窗口
root = Tk.Tk()
root.title('pchome downloader')
ft = Font(family = ('Verdana'), size = 8 ) #字体

frame1 = Tk.Frame(root)
accountLabel = Tk.Label(frame1, text="account:")
accountEntry = Tk.Entry(frame1, font=ft)
pwdLabel = Tk.Label(frame1, text="default password:")
pwdEntry = Tk.Entry(frame1, font=ft)

def lookup():
    username = accountEntry.get()
    getAlbumList(username)
    for elem in elements:
        createAlbumEntry(root, elem)

lookupButton = Tk.Button(frame1, text="look", command=lookup)

def download():
    username = accountEntry.get()
    pwd = pwdEntry.get()
    downAlbum(username, pwd)

downloadButton = Tk.Button(frame1, text="download", command=download)

accountLabel.pack(side=Tk.LEFT)
accountEntry.pack(side=Tk.LEFT)

downloadButton.pack(side=Tk.RIGHT)
lookupButton.pack(side=Tk.RIGHT)
pwdEntry.pack(side=Tk.RIGHT)
pwdLabel.pack(side=Tk.RIGHT)

frame1.pack(side=Tk.TOP)

Tk.mainloop()
