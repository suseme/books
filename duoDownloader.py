#!/usr/bin/python
# coding=utf8

import sys
import os
import wx
import subprocess
import threading
import time

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
			
class DuokanDownloaderWnd(wx.Frame):
	def __init__(self, tt):
		wx.Frame.__init__(self, None, title=tt, size=(640,250))

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

		self.redir = RedirectText(self)
		sys.stdout = self.redir

	def add_log(self, log):
		self.teInfo.AppendText(log)

	def OnKeyDown(self, event):
		self.start(event)

	def start(self, event):
		self.gauge.SetValue(10);
		self.teInfo.Clear()

		bid = str(self.teId.GetValue())
		name = str(self.teName.GetValue())
		print 'ID: %s' % bid
		print 'Name: %s' % name
		
		cmd = ["duokan.bat", bid, name]

		print 'downloading...'
		print '---------'
		self.pip = subprocess.Popen(cmd, bufsize=0, stdout=subprocess.PIPE)

		self.logging = Logging()
		self.logging.setPip(self.pip)
		self.logging.start()

		self.gauge.SetValue(100);

		self.btnDownload.Disable()
		self.btnStop.Enable()

	def stop(self, event):
		self.logging.stop()
		self.pip.kill()
		self.btnDownload.Enable()
		self.btnStop.Disable()
		
	def setId(self, id):
		self.teId.SetValue(id)
		
	def setName(self, name):
		self.teName.SetValue(name)
		
class RedirectText:
	def __init__(self, wnd):
		self.wnd=wnd

	def write(self, string):
		# self.wnd.AppendText("%s" % string.decode("UTF-8"))
		# self.wnd.WriteText("%s" % string.decode("UTF-8"))
		# wx.CallAfter(self.wnd.add_log, "%s" % string.decode("UTF-8"))
		wx.CallAfter(self.wnd.add_log, string)
		# self.wnd.add_log(string)

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