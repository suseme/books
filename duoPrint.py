import sys, wx, string


class DuokanPrintWnd(wx.Frame):
	def __init__(self, tt):
		wx.Frame.__init__(self, None, title=tt)
		
		panel = wx.Panel(self)
		
		types = ['2x2','1x2']
		
		lblTypes=wx.StaticText(panel, -1, "Types: ", style=1)
		self.cbTypes = wx.ComboBox(panel, -1, types[0], (15, 30), wx.DefaultSize, types, wx.CB_DROPDOWN)
		lblPages=wx.StaticText(panel, -1, "Pages: ", style=1)
		self.tePages = wx.TextCtrl(panel)
		btnGenerate = wx.Button(panel, label='Generate')
		btnGenerate.Bind(wx.EVT_BUTTON, self.generate)
		self.tePages.Bind(wx.EVT_TEXT_ENTER, self.OnKeyDown)

		hbox = wx.BoxSizer()
		hbox.Add(lblTypes, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
		hbox.Add(self.cbTypes, proportion=0, flag=wx.EXPAND, border=5)
		hbox.Add(lblPages, proportion=0, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
		hbox.Add(self.tePages, proportion=1, flag=wx.EXPAND);
		hbox.Add(btnGenerate, proportion=0, flag=wx.LEFT, border=5)

		self.teLog = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_LINEWRAP | wx.TE_WORDWRAP)
		
		vbox = wx.BoxSizer(wx.VERTICAL);
		vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
		vbox.Add(self.teLog, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
		
		panel.SetSizer(vbox)
		
		self.redir = RedirectText(self)
		sys.stdout = self.redir
		
	def OnKeyDown(self, event):
		self.generate(event)
		
	def generate(self, event):
		self.teLog.Clear()
		
		types = self.cbTypes.GetSelection()
		pages = string.atoi(self.tePages.GetValue())
		if types == 1:
			self.prnt1_2(pages)
		else:
			self.prnt2_2(pages)
		
	def prnt2_2(self, pages):
		max = ((pages + 7) / 8) * 8
		for i in range(1, max + 1):
			page = 1
			if i % 8 == 1:
				page = i + 3
			elif i % 8 == 2:
				page = i - 1
			elif i % 8 == 3:
				page = i + 5
			elif i % 8 == 4:
				page = i + 1
			elif i % 8 == 5:
				page = i - 3
			elif i % 8 == 6:
				page = i - 3
			elif i % 8 == 7:
				page = i - 1
			elif i % 8 == 0:
				page = i - 1
			else:
				print 'error...'
				break

			if page < pages:
				sys.stdout.write('%d,' % page)
			else:
				sys.stdout.write('%d,' % pages)

	def prnt1_2(self, pages):
		max = ((pages + 3) / 4) * 4
		for i in range(1, max + 1):
			page = 1
			if i % 4 == 1:
				page = i + 3
			elif i % 4 == 2:
				page = i - 1
			elif i % 4 == 3:
				page = i - 1
			elif i % 4 == 0:
				page = i - 1
			else:
				print 'error...'
				break

			if page < pages:
				sys.stdout.write('%d,' % page)
			else:
				sys.stdout.write('%d,' % pages)

	def logger(self, str):
		self.teLog.AppendText(str);

class RedirectText:
	def __init__(self, wnd):
		self.wnd=wnd

	def write(self, string):
		# self.wnd.AppendText("%s" % string.decode("UTF-8"))
		# self.wnd.WriteText("%s" % string.decode("UTF-8"))
		# wx.CallAfter(self.wnd.add_log, "%s" % string.decode("UTF-8"))
		wx.CallAfter(self.wnd.logger, string)

def usage(name):
	print '%s [type] pages' % name
	print 'type 1|2'
	
if __name__ == '__main__':
	app = wx.App(0)
	win = DuokanPrintWnd('Book printer')
	win.Show(True)
	app.MainLoop()