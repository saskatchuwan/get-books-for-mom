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
  proxies = proxy.get_proxies()

  successful = False
  attempt = 1
  response = None

  while successful == False and attempt <= 50:
    try:
      print("Request #%d"%attempt)

      print(headers)
      print(proxies)

      attempt += 1
      response = requests.get(url, headers=headers, proxies=proxies, timeout=3)
      # print(response.text)
      successful = True
    except:
      headers = proxy.get_headers()
      proxies = proxy.get_proxies()
      print("Skipping. Connnection error")

  return BeautifulSoup(response.text, "html.parser")

  # time.sleep(random.random() * 5 + 1.0)
	# user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
	# response = requests.get(url, headers={'User-Agent': user_agent})
	# return BeautifulSoup(response.text, 'html.parser')

def div_with_content(div):
  return len(div.findAll('p')) > 0


if __name__ == "__main__":
    print(get_beautiful_soup_html('http://tw.zhsxs.com/'))