# # # #!/usr/bin/python

import sys, re, os, wx
from datetime import *
from urlparse import urlparse
from bs4 import BeautifulSoup
from spider import Spider, Persist

reload(sys)
sys.setdefaultencoding('utf8')

class DuokanSpecial:
	siteRoot = 'http://www.duokan.com'

	def __init__(self, wnd=None):
		self.titles = {}
		self.links = {}
		self.authors = {}

		self.callbacks = {'http://www.duokan.com/special':self.findBooks, 'http://www.duokan.com':self.findLinks}
		self.spider = Spider('Duokan Special')
		self.spider.add_callbacks(self.callbacks)
		self.spider.add_urls([DuokanSpecial.siteRoot])
		self.wnd = wnd

	def findLinks(self, url, response):
		self.soup = BeautifulSoup(response, from_encoding='utf8')
		list_nodes = self.soup.findAll('div', attrs={'class':'u-aimg'})
		if len(list_nodes) > 0:
			list_node = list_nodes[0]
			link = list_node.findAll('a')[0]
			link = [DuokanSpecial.siteRoot + link['href']]
			self.spider.add_urls(link)
			if self.wnd:
				wx.CallAfter(self.wnd.setUrl, link[0])

	def findBooks(self, url, response):
		self.soup = BeautifulSoup(response, from_encoding='utf8')
		book_nodes = self.soup.findAll('li', attrs={'class':'u-bookitm1 j-bookitm'})
		for item in book_nodes:
			id = item['data-id']
			if id:
				title = item.find('a', attrs={'class':'title'}).string
				link = item.find('a', attrs={'class':'title'})['href']
				author = item.find('div', attrs={'class':'u-author'}).find('span').string
				self.titles[id] = title
				self.links[id] = DuokanSpecial.siteRoot + link
				self.authors[id] = author
				if self.wnd:
					wx.CallAfter(self.wnd.appendItem, id, self.titles[id], self.authors[id], self.links[id])
		return self.titles

	def start(self):
		self.spider.start()

		
	def getTitle(self):
		return self.titles
		
	def getLinks(self):
		return self.links
		
	def getAuthors(self):
		return self.authors

if __name__ == "__main__":
	special = DuokanSpecial()
	special.start()

