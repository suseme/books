#!/usr/bin/python
# coding=utf8

__author__ = 'vin@misday.com'

import os
import wx
from duoSpider import Special
from duoMain import Duokan, Downloader

class MainWindow(wx.Frame):
    PROXY_HOST = ''
    PROXY_AUTH_USER = ''
    PROXY_AUTH_PSWD = ''
    PROXY_AUTH = '%s:%s' % (PROXY_AUTH_USER, PROXY_AUTH_PSWD)

    BG_FREED = wx.Colour(255, 255, 153)
    BG_DOWN = wx.Colour(146, 208, 80)

    COLUMNS = ['#', 'ID', 'TITLE', 'AUTHOR', 'LINK', 'PROGRESS']
    (COLUMN_NUM, COLUMN_ID, COLUMN_TITLE, COLUMN_AUTHOR, COLUMN_LINK, COLUMN_PROGRESS) = range(0, 6)
    COLUMNS_WIDTH = [50, 200, 200, 200, 200, 100]

    MENUITEMS = ['&Fetch', '&Download all', '&Open in brower', '&Open download folder',
                 '&Clean tmp folder', '&Rename all', '&Crop', 'Crop for &printing', 'Crop for &kindle',
                 'Download', 'View in browser', 'Remove', 'Merge', 'Crop', 'Rename']
    (ID_MENUITEM_FETCH, ID_MENUITEM_DOWNLOAD_ALL, ID_MENUITEM_OPEN_IN_BROWER, ID_MENUITEM_OPEN_NEW,
     ID_MENUITEM_CLEAN_ALL, ID_MENUITEM_RENAME_ALL, ID_MENUITEM_CROP_SINGLE, ID_MENUITEM_CROP_4_PRINT, ID_MENUITEM_CROP_4_KINDLE,
     ID_MENUITEM_DOWN, ID_MENUITEM_VIEW, ID_MENUITEM_REMOVE, ID_MENUITEM_MERGE, ID_MENUITEM_CROP, ID_MENUITEM_RENAME,
     ID_BTN_FETCH, ID_BTN_OPEN, ID_BTN_DOWN, ID_LIST) = range(0, 19)

    def __init__(self, tt):
        self.duokan = Duokan()

        wx.Frame.__init__(self, None, title=tt, size=(1020, 800))

        #menu#################################
        # create a menu
        menuFile = wx.Menu()

        # add  menu item
        menuFile.Append(MainWindow.ID_MENUITEM_FETCH,           MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_FETCH])
        menuFile.Append(MainWindow.ID_MENUITEM_DOWNLOAD_ALL,    MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_DOWNLOAD_ALL])
        menuFile.AppendSeparator()
        menuFile.Append(MainWindow.ID_MENUITEM_OPEN_IN_BROWER,  MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_OPEN_IN_BROWER])
        menuFile.Append(MainWindow.ID_MENUITEM_OPEN_NEW,        MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_OPEN_NEW])

        # create a menu
        menuEdit = wx.Menu()
        menuEdit.Append(MainWindow.ID_MENUITEM_CLEAN_ALL,     MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_CLEAN_ALL])
        menuEdit.Append(MainWindow.ID_MENUITEM_RENAME_ALL,    MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_RENAME_ALL])
        menuEdit.AppendSeparator()
        menuEdit.Append(MainWindow.ID_MENUITEM_CROP_SINGLE,   MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_CROP_SINGLE])
        menuEdit.Append(MainWindow.ID_MENUITEM_CROP_4_PRINT,  MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_CROP_4_PRINT])
        menuEdit.Append(MainWindow.ID_MENUITEM_CROP_4_KINDLE, MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_CROP_4_KINDLE])

        # create menubar and add item
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        menuBar.Append(menuEdit, "&Edit")

        self.SetMenuBar(menuBar)
        self.CreateStatusBar()

        self.popupmenu = wx.Menu()
        self.popupmenu.Append(MainWindow.ID_MENUITEM_DOWN,   MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_DOWN])
        self.popupmenu.Append(MainWindow.ID_MENUITEM_VIEW,   MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_VIEW])
        self.popupmenu.Append(MainWindow.ID_MENUITEM_REMOVE, MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_REMOVE])
        self.popupmenu.Append(MainWindow.ID_MENUITEM_MERGE,  MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_MERGE])
        self.popupmenu.Append(MainWindow.ID_MENUITEM_CROP,   MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_CROP])
        self.popupmenu.Append(MainWindow.ID_MENUITEM_RENAME, MainWindow.MENUITEMS[MainWindow.ID_MENUITEM_RENAME])

        #panel######################################
        panel = wx.Panel(self)

        tsize = (20, 20)

        lblUrl=wx.StaticText(panel, -1, "Special URL: ", style=1)
        self.teUrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)

        btnUpdate = wx.BitmapButton(panel, MainWindow.ID_BTN_FETCH,     wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_BUTTON, tsize))
        btnBrowser = wx.BitmapButton(panel, MainWindow.ID_BTN_OPEN,     wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_BUTTON, tsize))
        btnDownload = wx.BitmapButton(panel, MainWindow.ID_BTN_DOWN,    wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_BUTTON, tsize))

        hbox = wx.BoxSizer()
        hbox.Add(btnUpdate, proportion=0, flag=wx.RIGHT, border=5)
        hbox.Add(lblUrl, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        hbox.Add(self.teUrl, proportion=1, flag=wx.EXPAND)
        hbox.Add(btnBrowser, proportion=0, flag=wx.LEFT, border=5)
        hbox.Add(btnDownload, proportion=0, flag=wx.LEFT, border=5)

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

        self.Bind(wx.EVT_MENU, self.onUpdate,       id=MainWindow.ID_MENUITEM_FETCH)
        self.Bind(wx.EVT_MENU, self.onBrowser,      id=MainWindow.ID_MENUITEM_OPEN_IN_BROWER)
        self.Bind(wx.EVT_MENU, self.onBrowserNew,   id=MainWindow.ID_MENUITEM_OPEN_NEW)
        self.Bind(wx.EVT_MENU, self.onDownload,     id=MainWindow.ID_MENUITEM_DOWNLOAD_ALL)

        self.Bind(wx.EVT_MENU, self.onClean,        id=MainWindow.ID_MENUITEM_CLEAN_ALL)
        self.Bind(wx.EVT_MENU, self.onRenameAll,    id=MainWindow.ID_MENUITEM_RENAME_ALL)
        self.Bind(wx.EVT_MENU, self.onCropSingle,   id=MainWindow.ID_MENUITEM_CROP_SINGLE)
        self.Bind(wx.EVT_MENU, self.onCrop4Print,   id=MainWindow.ID_MENUITEM_CROP_4_PRINT)
        self.Bind(wx.EVT_MENU, self.onCrop4Kindle,  id=MainWindow.ID_MENUITEM_CROP_4_KINDLE)

        self.Bind(wx.EVT_BUTTON, self.onUpdate,     id = MainWindow.ID_BTN_FETCH)
        self.Bind(wx.EVT_BUTTON, self.onBrowser,    id = MainWindow.ID_BTN_OPEN)
        self.Bind(wx.EVT_BUTTON, self.onDownload,   id = MainWindow.ID_BTN_DOWN)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,   self.onDownloadItem,    id=MainWindow.ID_LIST)
        self.Bind(wx.EVT_CONTEXT_MENU,          self.onShowPopup,       id=MainWindow.ID_LIST)

        self.Bind(wx.EVT_MENU, self.onDownloadItem, id=MainWindow.ID_MENUITEM_DOWN,     id2=MainWindow.ID_LIST)
        self.Bind(wx.EVT_MENU, self.onViewItem,     id=MainWindow.ID_MENUITEM_VIEW,     id2=MainWindow.ID_LIST)
        self.Bind(wx.EVT_MENU, self.onRenameItem,   id=MainWindow.ID_MENUITEM_RENAME,   id2=MainWindow.ID_LIST)
        self.Bind(wx.EVT_MENU, self.onRemoveItem,   id=MainWindow.ID_MENUITEM_REMOVE,   id2=MainWindow.ID_LIST)
        self.Bind(wx.EVT_MENU, self.onMerge,        id=MainWindow.ID_MENUITEM_MERGE,    id2=MainWindow.ID_LIST)
        self.Bind(wx.EVT_MENU, self.onCrop,         id=MainWindow.ID_MENUITEM_CROP,     id2=MainWindow.ID_LIST)

        self.downloadIdx = 0

        # self.redir = RedirectText(self)
        # sys.stdout = self.redir

        self.Centre()

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
        special = Special(MainWindow.PROXY_HOST, MainWindow.PROXY_AUTH_USER, MainWindow.PROXY_AUTH_PSWD)
        special.bind(Special.EVT_FIND_LINK, self.cbAddUrl)
        special.bind(Special.EVT_FIND_BOOK, self.cbAddBook)
        special.start()
        self.gauge.SetValue(100)

    def onBrowser(self, event):
        self.duokan.openInNewTab(self.teUrl.GetValue())

    def onBrowserNew(self, event):
        self.duokan.openNewFolder()

    def onDownload(self, event):
        self.downloadIdx = 0
        self.startDownload()

    def onClean(self, event):
        self.duokan.cleanTmp()

    def onRenameAll(self, event):
        self.duokan.renameAll()

    def onCropSingle(self, event):
        file_wildcard = "Pdf files(*.pdf)|*.pdf"
        dlg = wx.FileDialog(self,
                            'Open file to crop',
                            os.path.join(os.getcwd(), 'books'),
                            style = wx.OPEN,
                            wildcard = file_wildcard
                            )
        if dlg.ShowModal() == wx.ID_OK:
            filePath = dlg.GetPath()
            # print filePath
            self.duokan.cropSingle(filePath)
            retDlg = wx.MessageDialog(self,
                                    'Finished!',
                                    'Crop single',
                                    wx.OK)
            retDlg.ShowModal()
            retDlg.Destroy()
        dlg.Destroy()

    def onCrop4Print(self, event):
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
            self.duokan.crop4Print(filePath)
            retDlg = wx.MessageDialog(self,
                                    'Finished!',
                                    'Crop for printing',
                                    wx.OK)
            retDlg.ShowModal()
            retDlg.Destroy()
        dlg.Destroy()

    def onCrop4Kindle(self, event):
        file_wildcard = "Pdf files(*.pdf)|*.pdf"
        dlg = wx.FileDialog(self,
                            'Open file to crop for kindle',
                            os.path.join(os.getcwd(), 'books'),
                            style = wx.OPEN,
                            wildcard = file_wildcard
                            )
        if dlg.ShowModal() == wx.ID_OK:
            filePath = dlg.GetPath()
            print filePath
            self.duokan.crop4Kindle(filePath)
            retDlg = wx.MessageDialog(self,
                                    'Finished!',
                                    'Crop for kindle',
                                    wx.OK)
            retDlg.ShowModal()
            retDlg.Destroy()
        dlg.Destroy()

    # download a book
    def onDownloadItem(self,event):
        idx = self.list.GetFocusedItem()
        id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
        title = self.list.GetItemText(idx, MainWindow.COLUMN_TITLE)
        win = DownloaderWnd(title)
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
    def onViewItem(self, event):
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

    def onCrop(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
            self.duokan.crop(id)

    def onMerge(self, event):
        idx = self.list.GetFirstSelected()
        if idx != -1:
            id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
            self.duokan.merge(id)

    def startDownload(self):
        if self.downloadIdx < self.list.GetItemCount():
            id = self.list.GetItemText(self.downloadIdx, MainWindow.COLUMN_ID)
            self.down = Downloader(id, id, MainWindow.PROXY_HOST, MainWindow.PROXY_AUTH_USER, MainWindow.PROXY_AUTH_PSWD)
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

        # crop
        # id = self.list.GetItemText(self.downloadIdx, MainWindow.COLUMN_ID)

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
        notFreed = self.duokan.addBook(id, title, author, link)
        download = self.duokan.isDownload(id)
        wx.CallAfter(self.appendItem, id, title, author, link, (not notFreed), download)

class DownloaderWnd(wx.Frame):
	def __init__(self, tt=''):
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

			self.downloader = Downloader(bid, name, MainWindow.PROXY_HOST, MainWindow.PROXY_AUTH_USER, MainWindow.PROXY_AUTH_PSWD)
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