import requests
from bs4 import BeautifulSoup
import random

import proxy

HOMEPAGE = 'http://tw.zhsxs.com/'

def get_book_title(url):
  page = get_beautiful_soup_html(url)
  print("book title page ={}".format(page))
  h1 = page.find('div', {'id': 'novel_title'}).find('h1')
  return h1.text.strip()

def get_links_to_chapters(url):
  all_chapters_url = url.replace("zhsbook", "zhschapter")
  page = get_beautiful_soup_html(all_chapters_url)
  td_list = page.findAll('td', {'class': 'chapterlist'})

  links = []
  for row in td_list:
    a = row.find('a', href=True)
    link_suffix = a.attrs['href'] #Looks like /zhsread/29885_2639538.html
    link_suffix = link_suffix.strip("/")
    links.append(HOMEPAGE + link_suffix)
  return links

def get_beautiful_soup_html(url):
  headers = proxy.get_headers()
  response = requests.get(url, headers=headers)
  return BeautifulSoup(response.text, "html.parser")

def div_with_content(div):
  return len(div.findAll('p')) > 0
