#!/usr/bin/python
# coding=utf8

import sys
import os
import wx
import webbrowser
from duospider import DuokanSpecial
from duoDownloader import DuokanDownloaderWnd, Downloader
from duoPersist import Persist
from duoPdf import DuoPdf

class MainWindow(wx.Frame):
    COLUMNS = ['#', 'ID', 'TITLE', 'AUTHOR', 'LINK', 'PROGRESS']
    COLUMN_NUM=0
    COLUMN_ID=1
    COLUMN_TITLE=2
    COLUMN_AUTHOR=3
    COLUMN_LINK=4
    COLUMN_PROGRESS=5
    COLUMNS_WIDTH = [50, 200, 200, 200, 200, 100]

    BG_FREED = wx.Colour(255, 255, 153)
    BG_DOWN = wx.Colour(146, 208, 80)

    MENU_FETCH = 1
    MENU_OPEN_IN_BROWER = 2
    MENU_OPEN_NEW = 6
    MENU_DOWNLOAD_ALL = 3
    MENU_CLEAN_ALL = 4
    MENU_RENAME_ALL = 5
    MENU_PRINT_CROP = 7

    def __init__(self, tt):
        self.duokan = Duokan()

        wx.Frame.__init__(self, None, title=tt, size=(1020, 800))

        #menu#################################
        # create a menu
        menuFile = wx.Menu()

        # add  menu item
        menuFile.Append(MainWindow.MENU_FETCH, "&Fetch")
        menuFile.Append(MainWindow.MENU_DOWNLOAD_ALL, "&Download all")
        menuFile.AppendSeparator()
        menuFile.Append(MainWindow.MENU_OPEN_IN_BROWER, "&Open in brower")
        menuFile.Append(MainWindow.MENU_OPEN_NEW, "&Open download folder")

        # create a menu
        menuEdit = wx.Menu()
        menuEdit.Append(MainWindow.MENU_CLEAN_ALL,"&Clean tmp folder")
        menuEdit.Append(MainWindow.MENU_RENAME_ALL,"&Rename all")
        menuEdit.Append(MainWindow.MENU_PRINT_CROP, '&Crop for printing')

        # create menubar and add item
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        menuBar.Append(menuEdit, "&Edit")

        self.SetMenuBar(menuBar)
        self.CreateStatusBar()

        # add event
        self.Bind(wx.EVT_MENU, self.onUpdate, id=MainWindow.MENU_FETCH)
        self.Bind(wx.EVT_MENU, self.onBrowser, id=MainWindow.MENU_OPEN_IN_BROWER)
        self.Bind(wx.EVT_MENU, self.onBrowserNew, id=MainWindow.MENU_OPEN_NEW)
        self.Bind(wx.EVT_MENU, self.onDownload, id=MainWindow.MENU_DOWNLOAD_ALL)
        self.Bind(wx.EVT_MENU, self.onClean, id=MainWindow.MENU_CLEAN_ALL)
        self.Bind(wx.EVT_MENU, self.onRenameAll, id=MainWindow.MENU_RENAME_ALL)
        self.Bind(wx.EVT_MENU, self.onCropForPrint, id=MainWindow.MENU_PRINT_CROP)

        #panel######################################
        panel = wx.Panel(self)

        tsize = (20, 20)

        lblUrl=wx.StaticText(panel, -1, "Special URL: ", style=1)
        self.teUrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)

        # self.btnFetch = wx.Button(panel, label='FETCH')
        self.btnUpdate = wx.BitmapButton(panel, -1, wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_BUTTON, tsize))
        self.btnUpdate.Bind(wx.EVT_BUTTON, self.onUpdate)

        self.btnBrowser = wx.BitmapButton(panel, -1, wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_BUTTON, tsize))
        self.btnBrowser.Bind(wx.EVT_BUTTON, self.onBrowser)

        self.btnDownload = wx.BitmapButton(panel, -1, wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_BUTTON, tsize))
        self.btnDownload.Bind(wx.EVT_BUTTON, self.onDownload)

        self.btnClean = wx.BitmapButton(panel, -1, wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, wx.ART_BUTTON, tsize))
        self.btnClean.Bind(wx.EVT_BUTTON, self.onClean)

        hbox = wx.BoxSizer()
        hbox.Add(self.btnUpdate, proportion=0, flag=wx.RIGHT, border=5)
        hbox.Add(lblUrl, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        hbox.Add(self.teUrl, proportion=1, flag=wx.EXPAND)
        hbox.Add(self.btnBrowser, proportion=0, flag=wx.LEFT, border=5)
        hbox.Add(self.btnDownload, proportion=0, flag=wx.LEFT, border=5)
        hbox.Add(self.btnClean, proportion=0, flag=wx.LEFT, border=5)

        self.gauge = wx.Gauge(panel, -1, 100, style = wx.GA_PROGRESSBAR)
        self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.teInfo = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.HSCROLL)

        for i in range(len(MainWindow.COLUMNS)):
            self.list.InsertColumn(i, MainWindow.COLUMNS[i], width=MainWindow.COLUMNS_WIDTH[i])

        self.downloadIdx = 0

        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDownloadItem)
        self.list.Bind(wx.EVT_CONTEXT_MENU, self.onShowPopup)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.gauge, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.teInfo, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        panel.SetSizer(vbox)

        # self.redir = RedirectText(self)
        # sys.stdout = self.redir

        self.Centre()

        self.persist = Persist()
    def appendItem(self, id, title='', author='', link='', freed=False, done=False, progress='=========='):
        newIdx = self.list.GetItemCount()
        self.list.InsertStringItem(newIdx, '%d' % (newIdx + 1))
        self.list.SetStringItem(newIdx, MainWindow.COLUMN_ID, id)
        self.list.SetStringItem(newIdx, MainWindow.COLUMN_TITLE, title)
        self.list.SetStringItem(newIdx, MainWindow.COLUMN_AUTHOR, author)
        self.list.SetStringItem(newIdx, MainWindow.COLUMN_LINK, link)
        self.list.SetStringItem(newIdx, MainWindow.COLUMN_PROGRESS, progress)

        if freed:
            self.list.SetItemBackgroundColour(newIdx, MainWindow.BG_FREED)
        if done:
            self.list.SetItemBackgroundColour(newIdx, MainWindow.BG_DOWN)

        self.adjustListWidth()

    def adjustListWidth(self):
        self.list.SetColumnWidth(MainWindow.COLUMN_NUM, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(MainWindow.COLUMN_ID, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(MainWindow.COLUMN_TITLE, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(MainWindow.COLUMN_AUTHOR, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(MainWindow.COLUMN_LINK, wx.LIST_AUTOSIZE)
        self.list.SetColumnWidth(MainWindow.COLUMN_PROGRESS, wx.LIST_AUTOSIZE)

    # set download column progress
    def setProgress(self, idx, prog):
        if idx < self.list.GetItemCount():
            ppp = ''
            prog /= 10
            for i in range(prog):
                ppp += '>'
            for i in range(10 - prog):
                ppp += '='
            self.list.SetStringItem(idx, MainWindow.COLUMN_PROGRESS, ppp)

    def setUrl(self, url):
        self.teUrl.SetValue(url)

    def addLog(self, log):
        self.teInfo.AppendText(log)
        pass

    def onKeyDown(self, event):
        self.onUpdate(event)

    def onUpdate(self, event):
        self.gauge.SetValue(10)
        special = DuokanSpecial()
        special.bind(DuokanSpecial.ON_FIND_LINK, self.cbAddUrl)
        special.bind(DuokanSpecial.ON_FIND_BOOK, self.cbAddBook)
        special.start()
        self.gauge.SetValue(100)

    # for DuokanSpecial callback
    # def cbFindLink(self, event, link):
    #     wx.CallAfter(self.setUrl, link)
    #
    # # for DuokanSpecial callback
    # def cbFindBook(self, event, id, title, author, link):
    #     wx.CallAfter(self.appendItem, id, title, author, link)

    def onBrowser(self, event):
        self.duokan.openInNewTab(self.teUrl.GetValue())

    def onBrowserNew(self, event):
        path = os.path.join(os.path.curdir, 'books', 'new')
        self.duokan.openInNewTab(path)

    def onDownload(self, event):
        self.downloadIdx = 0
        self.startDownload()

    def onClean(self, event):
        self.duokan.clearTmp()

    def onRenameAll(self, event):
        path = os.path.join(os.path.curdir, 'books', 'new')
        for item in os.listdir(path):
            bid, extname = os.path.splitext(item)
            title = self.persist.getTitle(bid)
            newName =  '%s%s' % (title, extname)
            os.rename(os.path.join(path, item), os.path.join(path, newName))

    def onCropForPrint(self, event):
        file_wildcard = "Pdf files(*.pdf)|*.pdf"
        dlg = wx.FileDialog(self,
                            'Open file to crop for printing',
                            os.path.join(os.getcwd(), 'books'),
                            style = wx.OPEN,
                            wildcard = file_wildcard
                            )
        if dlg.ShowModal() == wx.ID_OK:
            filePath = dlg.GetPath()
            print filePath
            self.duokan.cropForPrint(filePath)
            retDlg = wx.MessageDialog(self,
                                    'Finished!',
                                    'Crop for printing',
                                    wx.OK)
            retDlg.ShowModal()
            retDlg.Destroy()
        dlg.Destroy()

    # download a book
    def onDownloadItem(self,event):
        idx = self.list.GetFocusedItem()
        id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
        title = self.list.GetItemText(idx, MainWindow.COLUMN_TITLE)
        win = DuokanDownloaderWnd(title)
        win.setId(id)
        win.setName(id)
        win.Show(True)

    # show popup menu
    def onShowPopup(self, event):
        self.popupmenu = wx.Menu()
        if self.list.GetFirstSelected() != -1:
            itemDown = self.popupmenu.Append(-1, 'Download')
            self.list.Bind(wx.EVT_MENU, self.onDownloadItem, itemDown)
            itemView = self.popupmenu.Append(-1, 'View in browser')
            self.list.Bind(wx.EVT_MENU, self.onViewItem, itemView)
            itemRename = self.popupmenu.Append(-1, 'Rename')
            self.list.Bind(wx.EVT_MENU, self.onRenameItem, itemRename)
            itemRemove = self.popupmenu.Append(-1, 'Remove')
            self.list.Bind(wx.EVT_MENU, self.onRemoveItem, itemRemove)
            itemCrop = self.popupmenu.Append(-1, 'Crop')
            self.list.Bind(wx.EVT_MENU, self.onCrop, itemCrop)
        pos = event.GetPosition()
        pos = self.list.ScreenToClient(pos)
        self.list.PopupMenu(self.popupmenu, pos)

    # open link in browser
    def onViewItem(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            url = self.list.GetItemText(idx, MainWindow.COLUMN_LINK)
            self.openInNewTab(url)

    # rename a item from id to title
    def onRenameItem(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
            title = self.list.GetItemText(idx, MainWindow.COLUMN_TITLE)
            self.duokan.rename(id, title)

    # delete an item
    def onRemoveItem(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            self.list.DeleteItem(idx)

    def onCrop(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
            self.duokan.crop(id)

    def startDownload(self):
        if self.downloadIdx < self.list.GetItemCount():
            id = self.list.GetItemText(self.downloadIdx, MainWindow.COLUMN_ID)
            self.down = Downloader(id, id)
            self.down.bind(Downloader.EVT_START, self.cbStart)
            self.down.bind(Downloader.EVT_STOP, self.cbStop)
            self.down.bind(Downloader.EVT_LOG, self.cbLog)
            self.down.bind(Downloader.EVT_PROG, self.cbProgress)
            self.down.start()

    # for downloader
    def cbStart(self, event):
        wx.CallAfter(self.setProgress, self.downloadIdx, 0)

    # for downloader
    def cbStop(self, event):
        # wx.CallAfter(self.setProgress, self.downloadIdx, 100)
        wx.CallAfter(self.gauge.SetValue, 100)

        # crop
        id = self.list.GetItemText(self.downloadIdx, MainWindow.COLUMN_ID)
        self.duokan.crop(id)

        # start next
        self.downloadIdx += 1
        self.startDownload()

    # for downloader
    def cbLog(self, event, str):
        wx.CallAfter(self.addLog, str)
        print str

    # for downloader
    def cbProgress(self, event, prog):
        # itemCount = self.list.GetItemCount()
        # wx.CallAfter(self.setProgress, self.downloadIdx, prog)
        wx.CallAfter(self.gauge.SetValue, prog)

    # for duoSpider
    def cbAddUrl(self, event, url):
        wx.CallAfter(self.setUrl, url)

    # for duoSpider
    def cbAddBook(self, event, id, title, author, link):
        notFreed = self.persist.addBook(id, title, author, link)
        download = self.persist.isDownload(id)
        wx.CallAfter(self.appendItem, id, title, author, link, (not notFreed), download)

class Duokan:
    def __init__(self):
        pass

    def crop(self, id):
        srcFile = os.path.join(os.path.curdir, 'books', 'new', id+'.pdf')
        destFile = os.path.join(os.path.curdir, 'books', 'new', id+'.pdf.pdf')
        duopdf = DuoPdf(srcFile)
        duopdf.cropWH(destFile, 500, 666)
        os.remove(srcFile)
        os.rename(destFile, srcFile)

    def cropForPrint(self, src):
        DuoPdf.duoCropForPrint(src)

    def rename(self, id, title):
        path = os.path.join(os.path.curdir, 'books', 'new', id+'.pdf')
        newPath = os.path.join(os.path.curdir, 'books', 'new', title+'.pdf')
        if os.path.exists(path):
            os.rename(path, newPath)

    # open in browser with new tab
    def openInNewTab(self, url):
        if len(url) > 0:
            webbrowser.open(url, new=2, autoraise=True)

    # clear the tmp dir
    def clearTmp(self):
        path = os.path.join(os.path.curdir, 'tmp')
        for item in os.listdir(path):
            filename = os.path.join(path, item)
            print 'deleting %s' % (filename,)
            self.delete_file_folder(filename)

    def delete_file_folder(self, src):
        '''delete files and folders'''
        if os.path.isfile(src):
            try:
                os.remove(src)
            except:
                pass
        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc=os.path.join(src,item)
                self.delete_file_folder(itemsrc)
            try:
                os.rmdir(src)
            except:
                pass

if __name__ == '__main__':
    app = wx.App(0)
    win = MainWindow("Book Downloader")
    win.Show(True)
    app.MainLoop()