#!/usr/bin/python
# coding=utf8

import sys
import os
import wx
import subprocess
import threading
import time
import webbrowser
from duospider import DuokanSpecial
from duoPrint import DuokanPrintWnd
from duoDownloader import DuokanDownloaderWnd

class Logging(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.running = True
		print 'Logging...'

	def setPip(self, pip):
		self.pip = pip

	def run(self):
		while self.running:
			buff = self.pip.stdout.readline()
			if buff == '' and self.pip.poll() != None:
				break
			print buff
		print 'Logging stop...'

	def stop(self):
		self.running = False
			
class MainWindow(wx.Frame):
	COLUMNS = ['#', 'ID', 'TITLE', 'AUTHOR', 'ACTION']
	COLUMN_NUM=0
	COLUMN_ID=1
	COLUMN_TITLE=2
	COLUMN_AUTHOR=3
	COLUMN_ACTION=4
	COLUMNS_WIDTH = [50, 250, 200, 200, 300]
	
	def __init__(self, tt):
		wx.Frame.__init__(self, None, title=tt, size=(1000, 600))

		panel = wx.Panel(self)

		lblUrl=wx.StaticText(panel, -1, "Special URL: ", style=1)
		self.teUrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		
		self.btnFetch = wx.Button(panel, label='FETCH')
		self.btnFetch.Bind(wx.EVT_BUTTON, self.onFetch)
		
		self.btnDownload = wx.Button(panel, label='BROWSE')
		self.btnDownload.Bind(wx.EVT_BUTTON, self.onBrowser)

		self.btnPrint = wx.Button(panel, label='PRINT')
		self.btnPrint.Bind(wx.EVT_BUTTON, self.onCalcPrint)
		

		hbox = wx.BoxSizer()
		hbox.Add(self.btnFetch, proportion=0, flag=wx.LEFT, border=5)
		hbox.Add(lblUrl, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
		hbox.Add(self.teUrl, proportion=1, flag=wx.EXPAND)
		hbox.Add(self.btnDownload, proportion=0, flag=wx.LEFT, border=5)
		hbox.Add(self.btnPrint, proportion=0, flag=wx.LEFT, border=5)

		self.gauge = wx.Gauge(panel, -1, 100, style = wx.GA_PROGRESSBAR)
		self.list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
		# self.teInfo = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.HSCROLL)
		
		for i in range(len(MainWindow.COLUMNS)):
			self.list.InsertColumn(i, MainWindow.COLUMNS[i], width=MainWindow.COLUMNS_WIDTH[i])

		self.listRow = 0
		
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDclick)
		self.list.Bind(wx.EVT_CONTEXT_MENU, self.onShowPopup)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
		vbox.Add(self.gauge, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
		vbox.Add(self.list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
		# vbox.Add(self.teInfo, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

		panel.SetSizer(vbox)

		# self.redir = RedirectText(self)
		# sys.stdout = self.redir
		
		self.Centre()

	def appendItem(self, id, title='', author='', link=''):
		self.list.InsertStringItem(self.listRow, '%d' % (self.listRow+1))
		self.list.SetStringItem(self.listRow, MainWindow.COLUMN_ID, id)
		self.list.SetStringItem(self.listRow, MainWindow.COLUMN_TITLE, title)
		self.list.SetStringItem(self.listRow, MainWindow.COLUMN_AUTHOR, author)
		self.list.SetStringItem(self.listRow, MainWindow.COLUMN_ACTION, link)
		self.listRow += 1
		
		self.list.SetColumnWidth(MainWindow.COLUMN_NUM, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(MainWindow.COLUMN_ID, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(MainWindow.COLUMN_TITLE, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(MainWindow.COLUMN_AUTHOR, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(MainWindow.COLUMN_ACTION, wx.LIST_AUTOSIZE)
		
	def setUrl(self, url):
		self.teUrl.SetValue(url)
		
	def addLog(self, log):
		# self.teInfo.AppendText(log)
		pass

	def onKeyDown(self, event):
		self.onFetch(event)

	def onFetch(self, event):
		self.gauge.SetValue(10);
		special = DuokanSpecial(self)
		special.start()
		self.gauge.SetValue(100);

	def onCalcPrint(self, event):
		win = DuokanPrintWnd('Book printer')
		win.Show(True)
		
	def onDclick(self,event):
		idx = self.list.GetFocusedItem()
		id = self.list.GetItemText(idx, MainWindow.COLUMN_ID)
		title = self.list.GetItemText(idx, MainWindow.COLUMN_TITLE)
		win = DuokanDownloaderWnd(title)
		win.setId(id)
		win.setName(id)
		win.Show(True)
	
	def onShowPopup(self, event):
		self.popupmenu = wx.Menu()
		if self.list.GetFirstSelected() != -1:
			item_down = self.popupmenu.Append(-1, 'Download')
			self.list.Bind(wx.EVT_MENU, self.onDclick, item_down)
			item_view = self.popupmenu.Append(-1, 'View')
			self.list.Bind(wx.EVT_MENU, self.onView, item_view)
		pos = event.GetPosition()
		pos = self.list.ScreenToClient(pos)
		self.list.PopupMenu(self.popupmenu, pos) 

	def onBrowser(self, event):
		self.openInNewTab(self.teUrl.GetValue())
		
	def onView(self, event):
		idx = self.list.GetFirstSelected()
		if idx != -1:
			url = self.list.GetItemText(idx, MainWindow.COLUMN_ACTION)
			self.openInNewTab(url)

	def openInNewTab(self, url):
		webbrowser.open(url, new=2, autoraise=True)

class RedirectText:
	def __init__(self, wnd):
		self.wnd=wnd

	def write(self, string):
		# self.wnd.AppendText("%s" % string.decode("UTF-8"))
		# self.wnd.WriteText("%s" % string.decode("UTF-8"))
		# wx.CallAfter(self.wnd.addLog, "%s" % string.decode("UTF-8"))
		wx.CallAfter(self.wnd.addLog, string)

if __name__ == '__main__':
	app = wx.App(0)
	win = MainWindow("Book Downloader")
	win.Show(True)
	app.MainLoop()