__author__ = 'vin@misday.com'

import os, webbrowser, ConfigParser
from vincore import Commading
from duoPdf import DuoPdf
from duoPersist import Persist
from duoLog import Log

class Duokan:
    def __init__(self):
        Duokan.ensureDir(os.path.join(os.path.curdir, 'tmp'))
        Duokan.ensureDir(os.path.join(os.path.curdir, 'books'))
        Duokan.ensureDir(os.path.join(os.path.curdir, 'books', 'new'))

        self.persist = Persist()

    def rename(self, id, title):
        path = os.path.join(os.path.curdir, 'books', 'new', id+'.pdf')
        newPath = os.path.join(os.path.curdir, 'books', 'new', title+'.pdf')
        if os.path.exists(path):
            os.rename(path, newPath)

    def openInNewTab(self, url):
        '''open in browser with new tab'''
        if len(url) > 0:
            webbrowser.open(url, new=2, autoraise=True)
        else:
            Log.e('url is empty')

    def cleanTmp(self):
        '''clean the tmp dir'''
        path = os.path.join(os.path.curdir, 'tmp')
        for item in os.listdir(path):
            filename = os.path.join(path, item)
            Log.e('deleting %s' % (filename, ))
            self.deleteFileFolder(filename)

    def deleteFileFolder(self, src):
        '''delete files and folders'''
        if os.path.isfile(src):
            try:
                os.remove(src)
            except:
                Log.e('delete [%s] failed...' % (src, ))
        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc=os.path.join(src,item)
                self.deleteFileFolder(itemsrc)
            try:
                os.rmdir(src)
            except:
                Log.e('delete [%s] failed...' % (src, ))

    def renameAll(self):
        path = os.path.join(os.path.curdir, 'books', 'new')
        for item in os.listdir(path):
            bid, extname = os.path.splitext(item)
            title = self.persist.getTitle(bid)
            if title:
                newName =  '%s%s' % (title, extname)
                os.rename(os.path.join(path, item), os.path.join(path, newName))

    def openNewFolder(self):
        path = os.path.join(os.path.curdir, 'books', 'new')
        self.openInNewTab(path)

    @staticmethod
    def ensureDir(path):
        '''check dir exist or not, create it if not exist'''
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def merge(id):
        '''merge pdf files in tmp/${id}, to books/new/${id}.pdf'''
        srcPath = os.path.join(os.path.curdir, 'tmp', id)
        destPath = os.path.join(os.path.curdir, 'books', 'new', id+'.pdf')
        DuoPdf.merge(destPath, srcPath)

    @staticmethod
    def mergeSingle(src):
        if not os.path.isdir(src):
            Log.w('[%s] is not a diractory, exit...' % (src, ))
            return
        path = os.path.split(src)
        id = path[1]
        destPath = os.path.join(path[0], id+'.pdf')
        DuoPdf.merge(destPath, src)

    @staticmethod
    def crop(id):
        '''crop pdf file in books/new/${id}.pdf'''
        srcPath = os.path.join(os.path.curdir, 'books', 'new', id+'.pdf')
        destPath = os.path.join(os.path.curdir, 'books', 'new', id+'.cropped.pdf')
        DuoPdf.cropWH(destPath, srcPath, 500, 666)
        os.remove(srcPath)
        os.rename(destPath, srcPath)

    @staticmethod
    def cropSingle(src):
        '''crop pdf file'''
        srcPath, ext = os.path.splitext(src)
        destPath = srcPath + '_c' + ext
        DuoPdf.cropWH(destPath, src, 500, 666)

    @staticmethod
    def crop4Print(src):
        '''crop blank edge except first page'''
        srcPath, ext = os.path.splitext(src)
        destPath = srcPath + '_p' + ext
        # print destPath
        DuoPdf.crop2(destPath, src, (0, 12, 48, 12), (48, 12, 0, 12))

    @staticmethod
    def crop4Kindle(src):
        '''crop blank edge'''
        srcPath, ext = os.path.splitext(src)
        destPath = srcPath + '_k' + ext
        # print destPath
        DuoPdf.crop(destPath, src, 50, 12, 50, 12)

    def addBook(self, id, title, author, link):
        return self.persist.addBook(id, title, author, link)

    def isDownload(self, id):
        return self.persist.isDownload(id)

class Downloader(Commading):
    EVT_LOG = 11
    EVT_PROG = 12
    EVT_START = Commading.ON_START
    EVT_STOP = 14

    def __init__(self, bid, name, proxyHost='', proxyAuthUser='', proxyAuthPswd=''):
        '''phantomjs --proxy=host --proxy-auth=username:password duokan.js %1 %ddd%/%2 4'''
        cmd = ['phantomjs',]
        if len(proxyHost) > 0:
            cmd.append('--proxy=%s' % (proxyHost, ))
            if len(proxyAuthUser) > 0 and len(proxyAuthPswd):
                cmd.append('--proxy-auth=%s:%s' % (proxyAuthUser, proxyAuthPswd))
        cmd.append('duokan.js')
        cmd.append(bid)
        cmd.append('tmp/%s' % (name, ))
        cmd.append('4')

        print cmd

        Commading.__init__(self, cmd)
        self.init([Downloader.EVT_LOG, Downloader.EVT_PROG, Downloader.EVT_START, Downloader.EVT_STOP])
        self.bind(Commading.ON_LOG, self.onLog)
        self.bind(Commading.ON_STOP, self.onStop)
        self.persist = Persist()
        self.id = bid

    def onStop(self, event):
        Log.i('phantomjs finished...')
        self.persist.setDownload(self.id)
        Duokan.merge(self.id)
        Log.i('merged pdf...')
        Duokan.crop(self.id)
        Log.i('croped pdf...')
        self.dispatch(Downloader.EVT_STOP)

    def onLog(self, event, str):
        # self.hdl.cbLog(str)
        self.dispatch(Downloader.EVT_LOG, str)
        prefix = 'progress, '
        if str.startswith(prefix):
            str = str[len(prefix):]
            str = str.lstrip('\n').lstrip('\r')
            str = str.split('/')
            prog = int(str[0]) * 100 / int(str[1])
            # self.hdl.cbProgress(prog)
            self.dispatch(Downloader.EVT_PROG, prog)

class Config:
    KEY_PROXY = 'proxy'
    KEY_PROXY_HOST = 'host'
    KEY_PROXY_USER = 'user'
    KEY_PROXY_PAWD = 'pswd'

    def __init__(self, name = 'config.conf'):
        self.conf = ConfigParser.ConfigParser()
        self.conf.read(name)

        self._getProxy()

    def _getProxy(self):
        self.host = ''
        self.user = ''
        self.pswd = ''
        try:
            self.host = self.conf.get(Config.KEY_PROXY, Config.KEY_PROXY_HOST)
            self.user = self.conf.get(Config.KEY_PROXY, Config.KEY_PROXY_USER)
            self.pswd = self.conf.get(Config.KEY_PROXY, Config.KEY_PROXY_PAWD)
        except:
            Log.w('read proxy failed')

    def getProxy(self):
        return (self.host, self.user, self.pswd)

