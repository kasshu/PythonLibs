#!/usr/bin/python
#encoding=utf8

"""
Open the specific url, decode the html into unicode
"""

import urllib2
import sys
import gzip
import StringIO
import chardet
import time
import re
import urlparse
#import pycurl
#import urllib3

timewait= 30
retrymax = 10

#NUM_SOCKETS = 20
#HEADER = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
#	  'connection':'keep-alive',
#         'Accept-encoding': 'gzip'}
#HTTP_PM = urllib3.PoolManager(num_pools=NUM_SOCKETS, headers=HEADER)

metaPattern = re.compile("<meta\\s+([^>]*http-equiv=[\"']?content-type[\"']?[^>]*)>", re.I)
charsetPattern = re.compile("charset=\\s*([a-z][_\\-0-9a-z]*)", re.I)
metacharsetPattern = re.compile("<meta.+charset=[\"']?\\s*([a-z][_\\-0-9a-z]*)[\"']?[^>]*>", re.I)

def getPageEncoding(content_type, html, defaultCharset):
	"""
	content_type: the Content-Type string in response header
	html: the html source code of the page
	defaultCharset: the default return value if python-chardet module cannot detect the encoding charset
	return: the encoding of the page
	"""
	charsets = set([])
	if content_type:
		m = re.search(charsetPattern, content_type)
		if m:
			charsets.add(m.group(1).lower())
	if html:
		temp = set([str.lower() for str in re.findall(metacharsetPattern, html)])
		charsets = charsets | temp
		for m in re.findall(metaPattern, html):
			temp = set([str.lower() for str in re.findall(charsetPattern, m)])
			charsets = charsets | temp
	if set(['gb2312', 'gbk']) <= charsets: 
		charsets.remove('gb2312')
        elif set(['gb2312']) == charsets: 
		charsets = set(['gbk'])
	if len(charsets) == 1:
		return charsets.pop()
	return getStrPossibleCharset(html, defaultCharset)


def getStrPossibleCharset(inputStr, defaultCharset):
	"""
	inputStr: the string to be detected
	defaulCharset: the default return value if python-chardet module cannot detect the encoding charset
	return: the encoding charset of the inputStr
	"""
	possibleCharset = defaultCharset
	encodingInfo = chardet.detect(inputStr)
	if (encodingInfo['confidence'] > 0.9):
		possibleCharset = encodingInfo['encoding']
	return possibleCharset;

def getHtmlByUrlWithProxy(url, defaultCharset, proxy):
	"""
	wrapper of getHtmlByUrl_urllib2
	"""
    	proxy_support = urllib2.ProxyHandler({'http':proxy})
    	opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
	return getHtmlByUrl_urllib2(url, defaultCharset, opener)

def getHtmlByUrl(url, defaultCharset):
	"""
	wrapper of getHtmlByUrl_urllib2
	"""
	return getHtmlByUrl_urllib2(url, defaultCharset, None)

def getHtmlByUrl_urllib2(url, defaultCharset, opener):
	"""
	url: the url to be got
	defaulCharset: the default encoding charset of the specific html
	opener: for proxy crawl, if you donot use proxy set it to None
	return: the unicode string stream of the html and the response url for redirect check
	"""
	retry_times = 0
	start_time = time.time()
	while retry_times < retrymax:
		try:
			request = urllib2.Request(url)
			hostname = urlparse.urlparse(url).hostname
			request.add_header('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')
			request.add_header('Accept-encoding', 'gzip')
			request.add_header('Referer', hostname)
			if opener:
				f = opener.open(request, timeout = timewait)
			else:
				f = urllib2.urlopen(request, timeout = timewait)
		except Exception as e:
			print 'Open failed: ' + url
			print e
			retry_times += 1
			continue
		try:
			data = f.read()
			response_url = f.geturl()
			if f.headers.get('Content-Encoding', None) == 'gzip':
				try:
					gf = gzip.GzipFile(fileobj=StringIO.StringIO(data))
					data = gf.read()
				except:
					print 'Gzip error! UrlReader return the extrabuf of gzip, url=%s'%(url,)
					data = gf.extrabuf
			content_type = f.headers.get('Content-Type', None)
			encoding = getPageEncoding(content_type, data, defaultCharset)
			value = data.decode(encoding, 'ignore')
		except Exception as e:
			print 'Decoding failed: ' + url
			print e
			retry_times += 1
			continue
		finally:
			f.close()
		end_time = time.time()
		#print "Time:", end_time - start_time, "url=", url
		return value, response_url
	print 'Retry max:' + url
	end_time = time.time()
	#print "Time:", end_time - start_time, "url=", url
	return None,None

###########################################################################################
#  The performance of urllib2 is enough, leave urllib3 and pycurl version for references  #
###########################################################################################

#def getHtmlByUrl_urllib3(url, defaultCharset):
#	"""
#	url: the url to be got
#	defaulCharset: the default encoding charset of the specific html
#	return: the unicode string stream of the html and the response url for redirect check
#	"""
#	retry_times = 0
#	start_time = time.time()
#	while retry_times < retrymax:
#		try:
#			r = HTTP_PM.request('GET', url, redirect = False,timeout = timewait)
#		except Exception as e:
#			print 'Open failed: ' + url
#			print e
#			retry_times += 1
#			continue
#		try:
#			data = r.data
#			if r.get_redirect_location():
#				response_url = r.get_redirect_location()
#			else:
#				response_url = url
#			content_type = r.getheader('Content-Type')
#			encoding = getPageEncoding(content_type, data, defaultCharset)
#			value = data.decode(encoding, 'ignore')
#		except Exception as e:
#			print 'Decoding failed: ' + url
#			print e
#			retry_times += 1
#			continue
#		finally:
#			r.release_conn()
#		end_time = time.time()
#		#print "Time:", end_time - start_time, "url=", url
#		return value, response_url
#	print 'Retry max:' + url
#	end_time = time.time()
#	#print "Time:", end_time - start_time, "url=", url
#	return None,None
#
#def getHtmlByUrl_pycurl(url, defaultCharset):
#	"""
#	url: the url to be got
#	defaulCharset: the default encoding charset of the specific html
#	return: the unicode string stream of the html and the response url for redirect check
#	"""
#	retry_times = 0
#	start_time = time.time()
#	while retry_times < retrymax:
#		try:
#			buffer = StringIO.StringIO() 
#			header = StringIO.StringIO() 
#			c = pycurl.Curl()
#			#set the target url
#			c.setopt(pycurl.URL, url.encode('utf8'))
#			#set http header
#			c.setopt(pycurl.HTTPHEADER, ['User-agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
#                                                     'Accept-encoding: gzip'])
#			#set buffer to be writen
#			c.setopt(pycurl.WRITEFUNCTION, buffer.write)
#			c.setopt(pycurl.HEADERFUNCTION, header.write)
#			#allow redirect
#			c.setopt(pycurl.FOLLOWLOCATION, 1)
#			c.setopt(pycurl.NOSIGNAL, 1)
#			#max redirect times
#			c.setopt(pycurl.MAXREDIRS, 5)
#			#connection time out
#			c.setopt(pycurl.CONNECTTIMEOUT, timewait)
#			#read from server time out
#			c.setopt(pycurl.TIMEOUT, timewait) 
#			c.perform()
#		except Exception as e:
#			print 'Open failed: ' + url
#			print e
#			retry_times += 1
#			continue
#		try:
#			data = buffer.getvalue()
#			response_url = c.getinfo(pycurl.EFFECTIVE_URL)
#			if 'Content-Encoding: gzip' in header.getvalue():
#				try:
#					gf = gzip.GzipFile(fileobj=StringIO.StringIO(data))
#					data = gf.read()
#				except:
#					print 'Gzip error! UrlReader return the extrabuf of gzip, url=%s'%(url,)
#					data = gf.extrabuf
#			content_type = c.getinfo(pycurl.CONTENT_TYPE)
#			encoding = getPageEncoding(content_type, data, defaultCharset)
#			value = data.decode(encoding, 'ignore')
#		except Exception as e:
#			print 'Decoding failed: ' + url
#			print e
#			retry_times += 1
#			continue
#		finally:
#			c.close()
#		end_time = time.time()
#		#print "Time:", end_time - start_time, "url=", url
#		return value, response_url
#	print 'Retry max:' + url
#	end_time = time.time()
#	#print "Time:", end_time - start_time, "url=", url
#	return None,None

if __name__ == "__main__":
	start = time.time()
	page, response_url = getHtmlByUrl('http://www.qidian.com/Book/1209977.aspx'.encode('utf8'), 'utf8')
	end = time.time()
	print 'Using pycurl:', end - start
	start = time.time()
	page, response_url = getHtmlByUrl_urllib2('http://www.qidian.com/Book/1209977.aspx', 'utf8')
	end = time.time()
	print 'Using urllib2:', end - start
	#print response_url
	#page, response_url = getHtmlByUrl('http://www.jjwxc.net/onebook.php?novelid=1590355', 'gbk')
	#print response_url
	#page, response_url = getHtmlByUrl('http://www.sogou.com/web?_ast=1355990110&sst0=1355990110400&p=40040100&sut=5527&w=01019900&_asf=www.sogou.com&query=%E6%AD%A6%E5%8A%A8%E4%B9%BE%E5%9D%A4+site%3Ajjwxc.net', 'gbk')
	#print response_url
	#page, response_url = getHtmlByUrl('http://dzxsw.com/book/100927/', 'utf8')
