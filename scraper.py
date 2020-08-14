import requests
from bs4 import BeautifulSoup
import random
import time

import proxy

def get_book_title(url):
  page = get_beautiful_soup_html(url)
  # print("book title page ={}".format(page))
  h1 = None

  try:
    if "tw.zhsxs.com" in url:
      h1 = page.find('div', {'id': 'novel_title'}).find('h1')

    if "tw.mingzw.net" in url:
      h1 = page.find('i', {'class': 'novel-name'})

  except:
    h1 = page.find('h1')

  return h1.text.strip()

def get_links_to_chapters(url, prefix, homepage):
  book = prefix + "book"
  chapter = prefix + "chapter"
  all_chapters_url = url.replace(book, chapter)
  page = get_beautiful_soup_html(all_chapters_url)

  links = []

  if "tw.mingzw.net" in url:
    link_list = page.find('div', {'class': 'content'}).find('ul').findAll('li')
    
  else:
    link_list = page.findAll('td', {'class': 'chapterlist'})

  for row in link_list:
    a = row.find('a', href=True)
    if a == None:
      continue
    link_suffix = a.attrs['href'] #Looks like /zhsread/29885_2639538.html
    link_suffix = link_suffix.strip("/")
    links.append(homepage + link_suffix)
  
  return links

# def get_beautiful_soup_html(url):
#   headers = proxy.get_headers()

#   successful = False
#   attempt = 1
#   response = None

#   while successful == False and attempt <= 50:
#     try:
#       time.sleep(random.random() * 5 + 1.0)
#       print("Request #%d"%attempt)
#       print(headers)

#       attempt += 1
#       response = requests.get(url, headers=headers, proxies=proxies, timeout=3)
#       # print(response.text)
#       successful = True
#     except:
#       headers = proxy.get_headers()
#       print("Skipping. Connnection error")

#   return BeautifulSoup(response.text, "html.parser")

def get_beautiful_soup_html(url):
  time.sleep(random.random() * 5 + 1.0)
  # user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
  user_agent = proxy.get_headers()
  # response = requests.get(url, headers={'User-Agent': user_agent})
  response = requests.get(url, headers=user_agent)
  return BeautifulSoup(response.text, 'html.parser')

def div_with_content(div):
  return len(div.findAll('p')) > 0
