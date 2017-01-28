#!/usr/bin/python
# coding=UTF-8

from __future__ import print_function
from HTMLParser import HTMLParser
import sys
import re
from itertools import izip

def log(*args, **kwargs):
		print(*args, file=sys.stderr, **kwargs)

class Converter(HTMLParser):
	State_Hyperspace = -2,
	State_Content = -1.
	State_Header = 0

	def in_hyperspace(self):
		return self.state == Converter.State_Hyperspace

	def in_content(self):
		return self.state == Converter.State_Content

	def in_header(self):
		return self.state >= Converter.State_Header

	def __init__(self):
		self.level = 0 
		self.para = -1
		self.state = -2
		self.parent_threads = []
		self.thread = 1		

		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		d_attrs = dict(attrs)
		d_style = None
		if 'style' in d_attrs:
			i = iter(re.split(';|:', d_attrs['style'].replace('\r\n', '')))
			d_style = dict(izip(i, i))

		if tag == 'p':
			self.para += 1
			self.state = Converter.State_Header if self.para % 2 == 0 else -1
			margin = ''
			
			if d_style != None and self.in_header() and self.para % 2 == 0:
				if 'margin-left' in d_style:
					margin = d_style['margin-left']

					if margin.endswith('pt'):
						margin_pt = float(margin[:-2])
					elif margin.endswith('in'):
						margin_pt = float(margin[:-2]) * 72

					level = int((margin_pt - 7.5) / 15)
				else:
					level = 1

				if level > self.level:
					if level != self.level + 1:
						log('Level mismatch: %d -> %d (%s)' % (self.level, level, margin))
					self.parent_threads.append(self.thread)
					self.level = level
				else:
					self.parent_threads.pop()
					while level < self.level:
						self.parent_threads.pop()
						print('</div>')
						self.level -= 1							
					self.parent_threads.append(self.thread)
					print('</div>')							

			if self.state < 0:
				print('<div class="content">')
		else:
			if self.para % 2 == 0:
				self.state += 1

		if self.state < 0:
			if tag == 'br':
				print('<br/>')

		if self.state == 1:
			print('<div class="comment level%d" id="thread%d""><div class="header">' % (self.level, self.thread))
			self.thread += 1

		if self.state == 8 and tag == 'a':
			print('<a href="%s">' % d_attrs['href'])

	def handle_endtag(self, tag):
		if tag == 'p':
			if self.in_header():
				if len(self.parent_threads) > 1:
					print('<a href="#thread%d">↑</a>' % self.parent_threads[-2])
				print('</div>')
			elif self.in_content():
				self.state = Converter.State_Hyperspace
				print('</div>')

	def handle_data(self, data):
		if self.in_content():
			print(data)
		elif self.state == 6:
			dt = data.replace('\r\n', '').replace('|', '')
			if len(dt) > 0:
				print(dt)
		elif self.state == 9:
			print(data + '</a>')

converter = Converter()
converter.feed(sys.stdin.read())


