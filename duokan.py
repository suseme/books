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
	COLUMNS = ['ID', 'TITLE', 'AUTHOR', 'ACTION']
	COLUMN_ID=0
	COLUMN_TITLE=1
	COLUMN_AUTHOR=2
	COLUMN_ACTION=3
	COLUMNS_WIDTH = [300, 200, 200, 300]
	
	def __init__(self, tt):
		wx.Frame.__init__(self, None, title=tt, size=(1000, 600))

		panel = wx.Panel(self)

		lblUrl=wx.StaticText(panel, -1, "Special URL: ", style=1)
		self.teUrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		
		self.btnGet = wx.Button(panel, label='GET')
		self.btnGet.Bind(wx.EVT_BUTTON, self.start)
		
		self.btnDownload = wx.Button(panel, label='BROWSE')
		self.btnDownload.Bind(wx.EVT_BUTTON, self.onBrowser)

		self.btnPrint = wx.Button(panel, label='Print')
		self.btnPrint.Bind(wx.EVT_BUTTON, self.calcPrint)
		

		hbox = wx.BoxSizer()
		hbox.Add(self.btnGet, proportion=0, flag=wx.LEFT, border=5)
		hbox.Add(lblUrl, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
		hbox.Add(self.teUrl, proportion=1, flag=wx.EXPAND)
		hbox.Add(self.btnDownload, proportion=0, flag=wx.LEFT, border=5)
		hbox.Add(self.btnPrint, proportion=0, flag=wx.LEFT, border=5)

		self.gauge = wx.Gauge(panel, -1, 100, style = wx.GA_PROGRESSBAR)
		self.lc = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
		# self.teInfo = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.HSCROLL)
		
		for i in range(len(MainWindow.COLUMNS)):
			self.lc.InsertColumn(i, MainWindow.COLUMNS[i])
		for i in range(len(MainWindow.COLUMNS_WIDTH)):
			self.lc.SetColumnWidth(i, MainWindow.COLUMNS_WIDTH[i])
		
		self.lcRow = 0
		
		self.lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnDclick)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
		vbox.Add(self.gauge, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
		vbox.Add(self.lc, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
		# vbox.Add(self.teInfo, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

		panel.SetSizer(vbox)

		# self.redir = RedirectText(self)
		# sys.stdout = self.redir

	def appendItem(self, id, title='', author='', link=''):
		self.lc.InsertStringItem(self.lcRow, id)
		self.lc.SetStringItem(self.lcRow, MainWindow.COLUMN_TITLE, title)
		self.lc.SetStringItem(self.lcRow, MainWindow.COLUMN_AUTHOR, author)
		self.lc.SetStringItem(self.lcRow, MainWindow.COLUMN_ACTION, link)
		self.lcRow += 1
		
	def setUrl(self, url):
		self.teUrl.SetValue(url)
		
	def addLog(self, log):
		# self.teInfo.AppendText(log)
		pass

	def OnKeyDown(self, event):
		self.start(event)

	def start(self, event):
		self.gauge.SetValue(10);
		special = DuokanSpecial(self)
		special.start()
		self.gauge.SetValue(100);

	def calcPrint(self, event):
		win = DuokanPrintWnd('Book printer')
		win.Show(True)
		
	def OnDclick(self,event):
		idx = self.lc.GetFocusedItem()
		id = self.lc.GetItemText(idx)
		title = self.lc.GetItemText(idx, MainWindow.COLUMN_TITLE)
		win = DuokanDownloaderWnd(title)
		win.setId(id)
		win.setName(id)
		win.Show(True)

	def onBrowser(self, event):
		webbrowser.open(self.teUrl.GetValue(), new=2, autoraise=True)

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