#!/usr/bin/python
# coding=UTF-8

from __future__ import print_function
from HTMLParser import HTMLParser
import sys

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Converter(HTMLParser):
	def __init__(self):
		self.level = 0
		self.parent_thread = 0
		self.current_thread = 0
		self.in_comment = False
		self.expect_link = False
		self.expect_time = False
		self.in_author = False
		HTMLParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		log('start ' + tag)

		attrs_dict = dict(attrs)
		self.expect_time = False
		
		if self.in_comment:
			print('<' + tag, end = " ")
			for attr, val in attrs:
				print(attr + '="' + val + '"', end = " ")
			print('>') 
			return
		if tag == 'ul':
			self.level += 1
			self.parent_thread = self.current_thread
		if tag == 'li':
			self.expect_link = True
			self.current_thread += 1
			print('<div class="comment level' + str(self.level) + '" id="thread' + str(self.current_thread) + '"">')
		if tag == 'p':
			self.in_comment = True
			print('<a href="#thread' + str(self.parent_thread) + '">↑</a>')
			print('</div>') # For header
			print('<div class="content">')
		if tag == 'a' and attrs_dict['class'] == 'user_name':
			print('<a class="author" href="' + attrs_dict['href'] + '">')
			self.in_author = True


	def handle_endtag(self, tag):
		log('end ' + tag)

		if tag == 'ul':
			self.level -= 1
		if tag == 'li':
			print('</div>')
		if tag == 'p':
			print('</div>')
			self.in_comment = False
		if tag == 'a' and self.expect_link:
			self.expect_time = True
			self.expect_link = False
		if self.in_comment:
			print('</' + tag + '>')
			return
		if self.in_author and tag == 'a':
			print('</a>')
			self.in_author = False

	def handle_data(self, data):
		log('data')

		if self.expect_time:
			print('<div class="header">' + data)
			self.expect_time = False
			return	

		if self.in_comment:
			print(data)
		if self.in_author:
			print(data)


converter = Converter()
converter.feed(sys.stdin.read())


