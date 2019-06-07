from get_proxies import get_proxies

from retrying import retry
from bs4 import BeautifulSoup
from newspaper import Article
from multiprocessing import Pool
from itertools import cycle

import requests
import random
import os
import time
import sys

HOMEPAGE = 'http://tw.zhsxs.com/'
DOWNLOAD_BATCH_SIZE = 2
CUSTOM_DELIMITER = "$$"

# This value gets changed and the only reason why it's global is because 
# Pythons multiprocessing pool doesn't support multiple arguments
OUTPUT_DIRECTORY = "./"

@retry(stop_max_attempt_number=3, wait_random_min=2000, wait_random_max=4000)
def parse_and_save_as_txt(url_with_index):
	# Wait for any time between 1 and 2 seconds.
  time.sleep(1.0 + random.random())	

  url, index = url_with_index.split(CUSTOM_DELIMITER)

  # NEWSPAPER- we use this in place of requests bc it handles foreign languages
  # To create an instance of article
  article = Article(url, language='zh')
  # To download an article
  article.download()
  # To parse an article
  article.parse()

  # REQUESTS
  page = get_beautiful_soup_html(url)
  print("page={}".format(page))


  # Create output filename
  index_prefix = index.zfill(8) #pad leading zeros until length of 8
  filename = index_prefix + article.title + ".txt"
  file_path = os.path.join(OUTPUT_DIRECTORY, filename)

	# Extract content
  content_soup = BeautifulSoup(article.html, 'html.parser')
  all_divs = content_soup.findAll('div')
  with open(file_path, 'w') as f:
    for div in all_divs:

      # Look for div containing paragraphs of text of the book
      if div_with_content(div):
        # When found, write only the text within the <p> tags
        f.write(div.text)
  print("Downloading {} COMPLETE!".format(filename))

def div_with_content(div):
	return len(div.findAll('p')) > 0


def get_beautiful_soup_html(url):
  time.sleep(random.random() * 5 + 1.0)
  user_agent = 'Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
  headers = {'User-Agent': user_agent}


  proxies = get_proxies()
  proxy_pool = cycle(proxies)

  for i in range(1,11):
    #Get a proxy from the pool
    proxy = next(proxy_pool)
    print("Request #%d"%i)
    try:
        response = requests.get(url,headers=headers, proxies={"http": proxy, "https": proxy})
        print(response.json())
    except:
        #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
        #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
        print("Skipping. Connnection error")

  return BeautifulSoup(response.text, 'html.parser')

def get_book_title(url):
  time.sleep(random.random() * 5)
  page = get_beautiful_soup_html(url)
  print("book title page ={}".format(page))
  h1 = page.find('div', {'id': 'novel_title'}).find('h1')
  return h1.text.strip()



def get_links_to_chapters(url):
  all_chapters_url = url.replace("zhsbook", "zhschapter")
  page = get_beautiful_soup_html(all_chapters_url)
  td_list =  page.findAll('td', {'class': 'chapterlist'})

  links = []
  for row in td_list:
    a = row.find('a', href=True)
    #strip a tag for just the href value
    link_suffix = a.attrs['href'] #Looks like /zhsbook/43070.html		
    link_suffix = link_suffix.strip("/")
    links.append(HOMEPAGE + link_suffix)
  return links



if __name__ == "__main__":
  # example command python get_books_for_mom_v2.py http://tw.zhsxs.com/zhsbook/29885.html 0

  book_index_link = sys.argv[1]
  start_from = int(sys.argv[2])

  # Get title of book
  title = get_book_title(book_index_link)
  print('got title={}'.format(title))

  if not HOMEPAGE in book_index_link: #ensures we're only using the zhsxs website
    print("This script only works for {}! exiting....".format(HOMEPAGE))
    sys.exit(1)

  # Make a directory for the book
  OUTPUT_DIRECTORY = os.path.join("./", title)
  os.mkdir(OUTPUT_DIRECTORY)

  # Get chapters
  links_to_chapters = get_links_to_chapters(book_index_link)
  print('links to chapters={}'.format(links_to_chapters))
  links_with_index = []
  for i in range(start_from, len(links_to_chapters)):
    links_with_index.append(links_to_chapters[i] + CUSTOM_DELIMITER + str(i))

  print('links to chapters with index={}'.format(links_with_index))

  # Download all the chapters in parallel batches	
  pool = Pool(DOWNLOAD_BATCH_SIZE)
  pool.map(parse_and_save_as_txt, links_with_index)
  pool.close()
  pool.join()
  parse_and_save_as_txt('http://tw.zhsxs.com/zhsread/29885_2639617.html$$80')

