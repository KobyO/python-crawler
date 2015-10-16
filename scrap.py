#!/usr/bin/python
# Copyright 2015 soulaljean & bricedev.

import os
import sys
import re
import urllib2
import more_itertools
import csv
import time
from bs4 import BeautifulSoup

start_time = time.time()

OPENER = urllib2.build_opener()
OPENER.addheaders = [('User-agent', 'Mozilla/5.0')]
DICTIONARY = ["contact","about","kontakt","profile","propos","contacto"]

"""Fashion wordpress blog scrapping.
The purpose is to retrieve Fashion bloggers' mail address from wordpress fashion blogs."""

def get_urls(key_words):
  """Return a list urls using google search $key_words."""
  res = []
  url = "http://www.google.com/search?q=" + key_words + "&start=0" + "&num=10";
  response = OPENER.open(url)
  soup = BeautifulSoup(response.read(),"html.parser")
  for r in soup.findAll('a'):
    if ("url?q" in r["href"]) and ("webcache.googleusercontent.com" not in r["href"]):
      chaine = r["href"].encode("ISO-8859-1")
      chaine = chaine.split("&")[0].split("/url?q=")[1]
      res.append(chaine)
  response.close()
  print res
  return res

def get_dom(url):
  """Return the dom from the given url."""
  dom = ""
  try:
    response = OPENER.open(url)
    dom = response.read()
    response.close()
  except:
    pass
  return dom

def is_wordpress(string_dom):
  """Test if the given dom is powered by wordpress."""
  return True if string_dom.lower().find("wordpress") > 0 else False

def is_visited(url,visited_urls):
  """Test if the given url has been already visited."""
  return url.split("/")[2] in visited_urls

def get_email(dom):
  """try to retreive is wordpress website"""
  regexp_mail = "[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]{2,4}"
  return list(set(re.findall(regexp_mail, dom)))

def get_contact_url(dom):
  url_contact = ""
  soup = BeautifulSoup(dom,"html.parser")
  for a in soup.find_all('a'):
    if len(list(set(a.text.lower().split()).intersection(DICTIONARY))) > 0 :
      if not a.get('href') is None:
        url_contact = a.get('href')
  return url_contact

def visit(url):
  print "Processing =>> ", url
  mails = []
  dom = get_dom(url)
  mails = get_email(dom)
  if mails==[]:
    contact_url = get_contact_url(dom)
    if not contact_url == "":
      if not "http" in contact_url:
        contact_url = "http://" + url.split("/")[2] + url.split("/")[3] + contact_url    
      if url != contact_url:
        mails += visit(contact_url)
  return mails

def save_result_in_csv(collected_mails):
  """Save list result in CSV File"""
  csvfile = open('result.csv', "wb")
  writer = csv.writer(csvfile)
  for mail in collected_mails:
    writer.writerow([mail])

def main():
  key_words = sys.argv[1].replace(" ","%20")
  if not key_words:
    print 'invalid number of arguments'
    sys.exit(1)

  urls = get_urls(key_words)
  
  visited_urls = []
  collected_mails = []

  for url in urls:
    if not is_visited(url,visited_urls):
      collected_mails += visit(url)
      print "Number of collected mails", len(collected_mails)
      print ""
      visited_urls.append(url.split("/")[2])

  print(collected_mails)
  save_result_in_csv(collected_mails)
  print ""
  print "Time script : %s secondes" % (time.time() - start_time)
  print ""

if __name__ == '__main__':
  main()