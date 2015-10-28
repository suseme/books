__author__ = 'vince'

import threading
import subprocess
from .callbacks import Callbacks

class Commading(threading.Thread, Callbacks):
	ON_START = 1
	ON_STOP = 2
	ON_LOG = 3

	def __init__(self, cmd):
		threading.Thread.__init__(self)
		Callbacks.__init__(self)
		self.cmd = cmd
		self.running = True

		self.init([Commading.ON_START, Commading.ON_STOP, Commading.ON_LOG])

	def run(self):
		self.dispatch(Commading.ON_START)
		self.pip = subprocess.Popen(self.cmd, bufsize=0, stdout=subprocess.PIPE)

		while self.running:
			buf = self.pip.stdout.readline()
			if buf == '' and self.pip.poll() != None:
				break
			self.dispatch(Commading.ON_LOG, buf)
		self.dispatch(Commading.ON_STOP)
		self.running = False

	def stop(self):
		if self.running:
			self.running = False
			self.pip.kill()