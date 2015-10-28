# # # #!/usr/bin/python

import sys, re, os, wx
from datetime import *
from urlparse import urlparse
from bs4 import BeautifulSoup
from spider import Spider, Callbacks

reload(sys)
sys.setdefaultencoding('utf8')

class DuokanSpecial(Callbacks):
	siteRoot = 'http://www.duokan.com'

	ON_FIND_LINK = 1
	ON_FIND_BOOK = 2

	def __init__(self):
		Callbacks.__init__(self)
		self.init([DuokanSpecial.ON_FIND_LINK, DuokanSpecial.ON_FIND_BOOK])
		self.titles = {}
		self.links = {}
		self.authors = {}

		self.callbacks = {'http://www.duokan.com/special':self.findBooks, 'http://www.duokan.com/book':self.findBook, 'http://www.duokan.com':self.findLinks}
		self.spider = Spider('Duokan Special')
		self.spider.set_proxy('proxy-apac.delphiauto.net:8080', 'rzfwch', '4rfvcde3')
		self.spider.add_callbacks(self.callbacks)
		self.spider.add_urls([DuokanSpecial.siteRoot])

	def findLinks(self, url, response):
		self.soup = BeautifulSoup(response, from_encoding='utf8')
		list_nodes = self.soup.findAll('div', attrs={'class':'u-aimg'})
		if len(list_nodes) > 0:
			list_node = list_nodes[0]
			links = list_node.findAll('a')
			# limit free read
			link = links[0]
			link = [DuokanSpecial.siteRoot + link['href']]
			self.spider.add_urls(link)
			self.dispatch(DuokanSpecial.ON_FIND_LINK, link[0])
			# limit free buy
			link = links[2]
			link = [DuokanSpecial.siteRoot + link['href']]
			self.spider.add_urls(link)

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
				self.dispatch(DuokanSpecial.ON_FIND_BOOK, id, self.titles[id], self.authors[id], self.links[id])
		return self.titles

	def findBook(self, url, response):
		self.soup = BeautifulSoup(response, from_encoding='utf8')
		# id
		# content = self.soup.find('meta', attrs={'name':'apple-itunes-app'})['content'].split('/')
		# id = content[len(content) - 1]
		# title
		# descNode = self.soup.findAll('div', attrs={'class':'desc'})
		# title = descNode[0].find('h3').string
		# author
		author = ''
		# author = descNode[0].find('td', attrs={'class':'author'}).find('a').string
		# link
		# link = self.soup.find('div', attrs={'class':'cover', 'id':'cover-img'}).find('a')['href']
		# link = DuokanSpecial.siteRoot + link
		# self.dispatch(DuokanSpecial.ON_FIND_BOOK, id, title, author, link)

		scriptNodes = self.soup.findAll('script', attrs={'type':'text/javascript'})
		for node in scriptNodes:
			str = node.string
			if str:
				if str.find('window.dk_data') > 0:
					start = str.index('=') + len('=')
					end = str.index('window.dk_data.comments_url')
					str = str[start:end]
					# str = str.strip().lstrip()
					str = str.replace('book_id :', '\'book_id\' :')
					str = str.replace('book :', '\'book\' :')
					str = str.replace('sid :', '\'sid\' :')
					str = str.replace('id :', '\'id\' :')
					str = str.replace('title : ', '\'title\' : u')
					str = str.replace('old_price :', '\'old_price\' :')
					str = str.replace('price :', '\'price\' :')
					str = str.replace('cover :', '\'cover\' :')
					str = str.replace('url :', '\'url\' :')
					str = str.replace('webreader :', '\'webreader\' :')
					str = str.replace('limited_time :', '\'limited_time\' :')
					str = str.replace('authors : ', '\'authors\' : u')
					# print str
					dk_data = eval(str)
					id = dk_data['book']['id']
					title = dk_data['book']['title']
					author = dk_data['book']['authors']
					link = DuokanSpecial.siteRoot + dk_data['book']['url']
					self.dispatch(DuokanSpecial.ON_FIND_BOOK, id, title, author, link)

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

