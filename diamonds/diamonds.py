import urllib2
import re,sys
import datetime
from time import sleep
from random import random
from HTMLParser import HTMLParser

categories = ['sku', 'depth', 'table', 'girdle', 'symmetry', 'polish', 'culet',
           'fluorescence', 'measurements', 'lnwdthratio', 'shape',
           'pricepercarat', 'certlab', 'certpresent', 'nonmanufacturingdate',
           'manufacturingdate', 'price', 'clarity', 'color', 'cut', 'carat']

words = '''currency USD|sortCol date|shape RD|minCarat 1.00|maxCarat 10.00|
minColor H|maxColor D|minPrice 259|maxPrice 2600702|minCut Very+Good|
maxCut Signature+Ideal|minClarity VS2|maxClarity FL|minPolish VG|maxPolish EX|
minSymmetry VG|maxSymmetry EX|polish 1|fluorescence 5|symmetry 2|
looseDate false'''

class htmlParser(HTMLParser):
  global categories
  lines = None
  thisLine = None
  idx = -1
  newLine = False
  def handle_starttag(self, tag, attrs):
    attrsDir = {}
    for i in attrs: attrsDir[i[0]] = i[1]
    if not self.lines: self.lines = []
    if not self.thisLine: self.thisLine = [i for i in categories]
    if tag == 'div':
      if self.newLine and self.thisLine[0] != 'sku':
        self.lines.append(','.join(self.thisLine))
        self.thisLine = [i for i in categories]
        self.newLine = False
      if 'class' in attrsDir:
        classes = attrsDir['class'].split(' ')
        className = classes[-1]
        if classes[0] == "c1":
          self.newLine = True
        if className in categories:
          self.idx = categories.index(className)
      for i in attrsDir:
        if i in categories:
          if self.thisLine[categories.index(i)] != categories[categories.index(i)] and categories[categories.index(i)] == 'sku':
            raise Exception(','.join(self.thisLine))
          self.thisLine[categories.index(i)] = attrsDir[i].replace(',','')
  def handle_data(self, data):
    if self.idx != -1:
      self.thisLine[self.idx] = data.strip().replace(',','')
      self.idx = -1
          

def getPage(startIndex, testing=False):
  if testing: return open("diamonds.html", "r").read()
  global words
  ret = 'http://www.bluenile.com/diamond-search/grid.html?'
  ret += '&'.join(['='.join(i.split(' ')) for i in words.replace('\n','').split('|')])
  ret += '&type=SINGLE&startIndex=%d' % startIndex
  headers = { 'User-Agent': 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10' }
  req = urllib2.Request(ret, None, headers)
  return urllib2.urlopen(req).read()

def getCsv(startLine, pastLines=''):
  page = getPage(startLine)
  parser = htmlParser()
  parser.feed(page)
  lines = '\n'.join(parser.lines)
  return lines, len(parser.lines)

def getAll(filename):
  global categories
  start = now = datetime.datetime.now()
  startLine = 0
  f = open(filename, 'a+')
  line = ''
  if startLine == 0:
    line = ','.join(categories) 
  while len(line) > 0:
    now = datetime.datetime.now()
    seconds = (now - start).seconds
    if seconds % 30 == 0:
      print "Read %d lines in past %d seconds" % (startLine, seconds)
    f.write(line)
    f.write('\n')
    line, delta = getCsv(startLine, line)
    startLine += delta
    sleep(1)
  print 'Finished writing %s at %s' % (filename, str(now))

if __name__ == "__main__":
  now = datetime.datetime.now()
  filename = now.isoformat().replace('-','')[:8] + '.csv'
  filename = "/home/ubuntu/diamonds/data/%s" % filename
  open(filename, 'w+').close()
  getAll(filename)

