#!/usr/bin/python
# coding=utf8

import sys
import os
import wx
import time
from spider import Commading
from duoPersist import Persist

class Downloader(Commading):
	EVT_LOG = 11
	EVT_PROG = 12
	EVT_START = Commading.ON_START
	EVT_STOP = 14
	def __init__(self, bid, name):
		cmd = ["duokan.bat", bid, name]
		Commading.__init__(self, cmd)
		self.init([Downloader.EVT_LOG, Downloader.EVT_PROG, Downloader.EVT_START, Downloader.EVT_STOP])
		self.bind(Commading.ON_LOG, self.onLog)
		self.bind(Commading.ON_STOP, self.onStop)
		self.persist = Persist()
		self.id = bid

	def onStop(self, event):
		self.persist.setDownload(self.id)
		self.dispatch(event, Downloader.EVT_STOP)

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

class DuokanDownloaderWnd(wx.Frame):
	def __init__(self, tt=''):
		wx.Frame.__init__(self, None, title=tt, size=(640, 170))

		panel = wx.Panel(self)

		lblId=wx.StaticText(panel, -1, "ID: ", style=1)
		lblName=wx.StaticText(panel, -1, "Name: ", style=1)

		self.teId = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.teName = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		self.btnDownload = wx.Button(panel, label='Run')
		self.btnDownload.Bind(wx.EVT_BUTTON, self.start)

		self.btnStop = wx.Button(panel, label='Stop')
		self.btnStop.Bind(wx.EVT_BUTTON, self.stop)
		self.btnStop.Disable()

		self.teName.Bind(wx.EVT_TEXT_ENTER, self.OnKeyDown)

		hbox = wx.BoxSizer()
		hbox.Add(lblId, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
		hbox.Add(self.teId, proportion=1, flag=wx.EXPAND)
		hbox.Add(lblName, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
		hbox.Add(self.teName, proportion=1, flag=wx.EXPAND)
		hbox.Add(self.btnDownload, proportion=0, flag=wx.LEFT, border=5)
		hbox.Add(self.btnStop, proportion=0, flag=wx.LEFT, border=5)

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
		self.gauge.SetValue(10)
		self.teInfo.Clear()

		bid = str(self.teId.GetValue())
		name = str(self.teName.GetValue())
		self.addLog('ID: %s\n' % bid)
		self.addLog('Name: %s\n' % name)

		self.addLog('downloading...\n')
		self.addLog('---------\n')

		self.downloader = Downloader(bid, name)
		self.downloader.bind(Downloader.ON_STOP, self.cbStop)
		self.downloader.bind(Downloader.EVT_LOG, self.cbLog)
		self.downloader.bind(Downloader.EVT_PROG, self.cbProgress)
		self.downloader.start()

		# self.gauge.SetValue(100);
	
		self.btnDownload.Disable()
		self.btnStop.Enable()

	def stop(self, event):
		self.downloader.stop()
		self.btnDownload.Enable()
		self.btnStop.Disable()
		
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
	win = DuokanDownloaderWnd("Book Downloader")
	
	argc = len(sys.argv)
	if argc == 3:
		win.setId(sys.argv[1])
		win.setName(sys.argv[2])
	elif argc == 2:
		win.setId(sys.argv[1])
		win.setName(sys.argv[1])
	win.Show(True)
	app.MainLoop()