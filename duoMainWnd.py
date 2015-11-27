#!/usr/bin/python
# coding=utf8

__author__ = 'vin@misday.com'

import os
import wx
from pyvin import ux
from duoSpider import Special
from duoMain import Duokan, Downloader, Config

class MainWindow(wx.Frame):
    tsize = (20, 20)

    BG_FREED = wx.Colour(255, 255, 153)
    BG_DOWN = wx.Colour(146, 208, 80)

    (ID_MENUITEM_FETCH, ID_MENUITEM_DOWNLOAD_ALL, ID_MENUITEM_OPEN_IN_BROWER, ID_MENUITEM_OPEN_NEW, ID_MENUITEM_SHUTDOWN,
     ID_MENUITEM_CLEAN_TMP, ID_MENUITEM_RENAME_ALL, ID_MENUITEM_MERGE_SINGLE, ID_MENUITEM_CROP_SINGLE, ID_MENUITEM_CROP_4_PRINT, ID_MENUITEM_CROP_4_KINDLE,
     ID_MENUITEM_DOWN, ID_MENUITEM_VIEW, ID_MENUITEM_REMOVE, ID_MENUITEM_MERGE, ID_MENUITEM_CROP, ID_MENUITEM_RENAME,
     ID_LIST,
     ID_TOOL_FETCH, ID_TOOL_OPEN, ID_TOOL_DOWN) = range(0, 21)

    COLUMNS = ['#', 'ID', 'TITLE', 'AUTHOR', 'LINK', 'PROGRESS']
    (COLUMN_NUM, COLUMN_ID, COLUMN_TITLE, COLUMN_AUTHOR, COLUMN_LINK, COLUMN_PROGRESS) = range(0, 6)
    COLUMNS_WIDTH = [50, 200, 200, 200, 200, 100]

    def __init__(self, tt):
        self.duokan = Duokan()
        self.conf = Config()

        self.MENUBAR = [('&File', (
                                ('&Fetch',                  '', MainWindow.ID_MENUITEM_FETCH,           self.onUpdate),
                                ('&Download all',           '', MainWindow.ID_MENUITEM_DOWNLOAD_ALL,    self.onDownloadAll),
                                ("", '', '', ""),
                                ('&Open in brower',         '', MainWindow.ID_MENUITEM_OPEN_IN_BROWER,  self.onBrowser),
                                ('&Open download folder',   '', MainWindow.ID_MENUITEM_OPEN_NEW,        self.onOpenNewFolder),
                                ("", '', '', ""),
                                ('Shutdown after finish',   '', MainWindow.ID_MENUITEM_SHUTDOWN,        self.menuShutdown, wx.ITEM_CHECK),
                         )),
                        ('&Edit', (('&Clean tmp folder',     '', MainWindow.ID_MENUITEM_CLEAN_TMP,      self.onCleanTmp),
                                   ('&Rename all',           '', MainWindow.ID_MENUITEM_RENAME_ALL,     self.onRenameAll),
                                   ("", "", '', ""),
                                   ('&Merge',                 '', MainWindow.ID_MENUITEM_MERGE_SINGLE,  self.onMergeSingle),
                                   ('&Crop',                  '', MainWindow.ID_MENUITEM_CROP_SINGLE,   self.onCropSingle),
                                   ('Crop for &printing',     '', MainWindow.ID_MENUITEM_CROP_4_PRINT,  self.onCrop4Print),
                                   ('Crop for &kindle',       '', MainWindow.ID_MENUITEM_CROP_4_KINDLE, self.onCrop4Kindle)
                        ))
               ]

        self.POPMENU = [
            (MainWindow.ID_MENUITEM_DOWN,   'Download',         self.onDownloadItem,    MainWindow.ID_LIST),
            (MainWindow.ID_MENUITEM_VIEW,   'View in browser',  self.onBrowserItem,     MainWindow.ID_LIST),
            (MainWindow.ID_MENUITEM_REMOVE, 'Remove',           self.onRemoveItem,      MainWindow.ID_LIST),
            (MainWindow.ID_MENUITEM_MERGE,  'Merge',            self.onMergeItem,       MainWindow.ID_LIST),
            (MainWindow.ID_MENUITEM_CROP,   'Crop',             self.onCropItem,        MainWindow.ID_LIST),
            (MainWindow.ID_MENUITEM_RENAME, 'Rename',           self.onRenameItem,      MainWindow.ID_LIST)
        ]

        self.TOOLBAR = [
            (MainWindow.ID_TOOL_FETCH, 'Fetch',            wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_BUTTON, MainWindow.tsize),    self.onUpdate),
            (MainWindow.ID_TOOL_OPEN,  'View in browser',  wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_BUTTON, MainWindow.tsize),    self.onBrowser),
            (MainWindow.ID_TOOL_DOWN,  'Download all',     wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_BUTTON, MainWindow.tsize), self.onDownloadAll)
        ]

        wx.Frame.__init__(self, None, title=tt, size=(1020, 800))

        self.menubar = self.createMenubar()
        self.CreateStatusBar()
        self.createPopmenu()
        self.toolbar = self.createToolBar()

        #panel######################################
        panel = wx.Panel(self)

        lblUrl=wx.StaticText(panel, -1, "Special URL: ", style=1)
        self.teUrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)

        hbox = wx.BoxSizer()
        hbox.Add(lblUrl, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        hbox.Add(self.teUrl, proportion=1, flag=wx.EXPAND)

        self.gauge = wx.Gauge(panel, -1, 100, style = wx.GA_PROGRESSBAR)
        self.list = wx.ListCtrl(panel, MainWindow.ID_LIST, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.teInfo = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.HSCROLL)

        for i in range(len(MainWindow.COLUMNS)):
            self.list.InsertColumn(i, MainWindow.COLUMNS[i], width=MainWindow.COLUMNS_WIDTH[i])

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.gauge, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.teInfo, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,   self.onDownloadItem,    id=MainWindow.ID_LIST)
        self.Bind(wx.EVT_CONTEXT_MENU,          self.onShowPopup,       id=MainWindow.ID_LIST)

        self.downloadIdx = 0

        # self.redir = RedirectText(self)
        # sys.stdout = self.redir

        self.Centre()

    def createMenubar(self):
        menuBar = wx.MenuBar()
        for eachMenu in self.MENUBAR:
            label = eachMenu[0]
            items = eachMenu[1]
            menuBar.Append(self.createMenuItems(items), label)
        self.SetMenuBar(menuBar)
        return menuBar

    def createMenuItems(self, menuData):
        menu = wx.Menu()
        for item in menuData:
            if len(item) == 2:
                label = item[0]
                subMenu = self.createMenuItems(item[1])
                menu.AppendMenu(wx.ID_ANY, label, subMenu)
            else:
                label = item[0]
                help = item[1]
                id = item[2]
                handler = item[3]
                if len(item) > 4:
                    kind = item[4]
                else:
                    kind = wx.ITEM_NORMAL

                if label:
                    menu.Append(id, label, help, kind=kind)
                    self.Bind(wx.EVT_MENU, handler, id=id)
                else:
                    menu.AppendSeparator()
        return menu

    def createPopmenu(self):
        self.popupmenu = wx.Menu()
        for item in self.POPMENU:
            self.popupmenu.Append(item[0],   item[1])
            self.Bind(wx.EVT_MENU, item[2], id=item[0],     id2=item[3])
        return self.popupmenu

    def createToolBar(self):
        toolbar = self.CreateToolBar()
        for item in self.TOOLBAR:
            toolbar.AddLabelTool(item[0], item[1], item[2])
            self.Bind(wx.EVT_TOOL, item[3], id=item[0])
        toolbar.Realize()
        return toolbar

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
        proxy = self.conf.getProxy()
        special = Special(proxy[0], proxy[1], proxy[2])
        special.bind(Special.EVT_FIND_LINK, self.cbAddUrl)
        special.bind(Special.EVT_FIND_BOOK, self.cbAddBook)
        special.start()
        self.gauge.SetValue(100)

    def onBrowser(self, event):
        self.duokan.openInNewTab(self.teUrl.GetValue())

    def onOpenNewFolder(self, event):
        self.duokan.openNewFolder()

    def menuShutdown(self, event):
        print self.menubar.IsChecked(MainWindow.ID_MENUITEM_SHUTDOWN)

    def onDownloadAll(self, event):
        self.downloadIdx = 0
        self.startDownload()

    def onCleanTmp(self, event):
        self.duokan.cleanTmp()
        ux.showMsg(self, 'Finished', 'Clear tmp folder')

    def onRenameAll(self, event):
        self.duokan.renameAll()
        ux.showMsg(self, 'Finished', 'Rename All')

    def onMergeSingle(self, event):
        # file_wildcard = "Pdf files(*.pdf)|*.pdf"
        ret, filePath = ux.showDirDlg(self, 'Open dir to merge', os.path.join(os.getcwd(), 'tmp'))
        if ret and filePath:
            self.duokan.mergeSingle(filePath)
            ux.showMsg(self, 'Finished!', 'Merge single')

    def onCropSingle(self, event):
        file_wildcard = "Pdf files(*.pdf)|*.pdf"
        ret, filePath = ux.showFileDlg(self, 'Open file to crop', os.path.join(os.getcwd(), 'books'), file_wildcard)
        if ret and filePath:
            self.duokan.cropSingle(filePath)
            ux.showMsg(self,  'Finished!', 'Crop single')

    def onCrop4Print(self, event):
        file_wildcard = "Pdf files(*.pdf)|*.pdf"
        ret, filePath = ux.showFileDlg(self, 'Open file to crop for printing', os.path.join(os.getcwd(), 'books'), file_wildcard)
        if ret and filePath:
            self.duokan.crop4Print(filePath)
            ux.showMsg(self,  'Finished!', 'Crop for printing')

    def onCrop4Kindle(self, event):
        file_wildcard = "Pdf files(*.pdf)|*.pdf"
        ret, filePath = ux.showFileDlg(self, 'Open file to crop for printing', os.path.join(os.getcwd(), 'books'), file_wildcard)
        if ret and filePath:
            self.duokan.crop4Kindle(filePath)
            ux.showMsg(self,  'Finished!', 'Crop for kindle')

    # download a book
    def onDownloadItem(self,event):
        idx = self.list.GetFocusedItem()
        id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
        title = self.list.GetItemText(idx, MainWindow.COLUMN_TITLE)
        win = DownloaderWnd(self.conf, title)
        win.setId(id)
        win.setName(id)
        win.Show(True)

    # show popup menu
    def onShowPopup(self, event):
        if self.list.GetFirstSelected() != -1:
            pos = event.GetPosition()
            pos = self.list.ScreenToClient(pos)
            self.list.PopupMenu(self.popupmenu, pos)

    # open link in browser
    def onBrowserItem(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            url = self.list.GetItemText(idx, MainWindow.COLUMN_LINK)
            self.duokan.openInNewTab(url)

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

    def onCropItem(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
            self.duokan.crop(id)

    def onMergeItem(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
            self.duokan.merge(id)

    def startDownload(self):
        if self.downloadIdx < self.list.GetItemCount():
            id = self.list.GetItemText(self.downloadIdx, MainWindow.COLUMN_ID)
            proxy = self.conf.getProxy()
            self.down = Downloader(id, id, proxy[0], proxy[1], proxy[2])
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
        wx.CallAfter(self.setProgress, self.downloadIdx, 100)
        wx.CallAfter(self.gauge.SetValue, 100)
        self.list.SetItemBackgroundColour(self.downloadIdx, MainWindow.BG_DOWN)

        # start next
        self.downloadIdx += 1
        self.startDownload()

        if self.downloadIdx >= self.list.GetItemCount():
            if self.menubar.IsChecked(MainWindow.ID_MENUITEM_SHUTDOWN):
                os.system('shutdown -t 60 -f -s')

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
        notFreed = self.duokan.addBook(id, title, author, link)
        download = self.duokan.isDownload(id)
        wx.CallAfter(self.appendItem, id, title, author, link, (not notFreed), download)

class DownloaderWnd(wx.Frame):
    def __init__(self, conf, tt=''):
        self.conf = conf

        wx.Frame.__init__(self, None, title=tt, size=(640, 170))

        panel = wx.Panel(self)

        lblId=wx.StaticText(panel, -1, "ID: ", style=1)
        lblName=wx.StaticText(panel, -1, "Name: ", style=1)

        self.teId = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.teName = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.btnDownload = wx.ToggleButton(panel, label='Download')
        self.btnDownload.Bind(wx.EVT_TOGGLEBUTTON, self.start)

        self.teName.Bind(wx.EVT_TEXT_ENTER, self.OnKeyDown)

        hbox = wx.BoxSizer()
        hbox.Add(lblId, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        hbox.Add(self.teId, proportion=1, flag=wx.EXPAND)
        hbox.Add(lblName, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        hbox.Add(self.teName, proportion=1, flag=wx.EXPAND)
        hbox.Add(self.btnDownload, proportion=0, flag=wx.LEFT, border=5)

        self.teInfo = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.HSCROLL)
        self.gauge = wx.Gauge(panel, -1, 100, style = wx.GA_PROGRESSBAR)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.gauge, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.teInfo, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        panel.SetSizer(vbox)

    def OnExit(self, event):
        self.stop(event)
        self.Close(True)

    def OnKeyDown(self, event):
        self.start(event)

    def start(self, event):
        if self.btnDownload.GetValue():
            self.gauge.SetValue(10)
            self.teInfo.Clear()

            bid = str(self.teId.GetValue())
            name = str(self.teName.GetValue())
            self.addLog('ID: %s\n' % bid)
            self.addLog('Name: %s\n' % name)

            self.addLog('downloading...\n')
            self.addLog('---------\n')

            proxy = self.conf.getProxy()
            self.downloader = Downloader(bid, name, proxy[0], proxy[1], proxy[2])
            self.downloader.bind(Downloader.ON_STOP, self.cbStop)
            self.downloader.bind(Downloader.EVT_LOG, self.cbLog)
            self.downloader.bind(Downloader.EVT_PROG, self.cbProgress)
            self.downloader.start()
        else:
            self.downloader.stop()

    def stop(self, event):
        self.downloader.stop()

    def addLog(self, log):
        self.teInfo.AppendText(log)

    def cbStop(self, event):
        wx.CallAfter(self.gauge.SetValue, 100)

    def cbLog(self, event, str):
        wx.CallAfter(self.addLog, str)

    def cbProgress(self, event, prog):
        wx.CallAfter(self.gauge.SetValue, prog)

    def setId(self, id):
        self.teId.SetValue(id)

    def setName(self, name):
        self.teName.SetValue(name)

if __name__ == '__main__':
    app = wx.App(0)
    win = MainWindow('Book Downloader')
    win.Show(True)
    app.MainLoop()