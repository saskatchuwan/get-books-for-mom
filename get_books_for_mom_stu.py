from multiprocessing import Pool
from retrying import retry
import requests
from bs4 import BeautifulSoup
import random
import time

import random
import os
import time
import sys

import proxy

HOMEPAGES = ['http://www.stu.la/', 'https://www.qkxsy.com/']
DOWNLOAD_BATCH_SIZE = 3
CUSTOM_DELIMITER = "$$"

# This value gets changed and the only reason why it's global is because 
# Pythons multiprocessing pool doesn't support multiple arguments
OUTPUT_DIRECTORY = "./"

@retry(stop_max_attempt_number=3, wait_random_min=2000, wait_random_max=4000)
def parse_and_save_as_text(url_with_index):
	# Wait for any time between 1 and 2 seconds.
  time.sleep(1.0 + random.random())	

  url, index, book_directory = url_with_index.split(CUSTOM_DELIMITER)

  # REQUEST
  article = get_beautiful_soup_html(url)

  # Create output filename
  article_title = article.find('h1').text.strip()

  # book_directory = article.find('title').text.split('_')[0]
  
  index_prefix = index.zfill(8) #pad leading zeros until length of 8
  filename = index_prefix + article_title + ".txt"
  file_path = os.path.join(OUTPUT_DIRECTORY, book_directory, filename)

  with open(file_path, 'w') as f:
    div_with_content = None
    if "qkxsy" in url:
      div_with_content = article.find('div', {'id': 'chaptercontent'})
    else:
      div_with_content = article.find('div', {'id': 'BookText'})

    f.write(div_with_content.text)

  print("Downloading {} COMPLETE!".format(filename))

def get_links_to_chapters(url, homepage):
  page = get_beautiful_soup_html(url)

  links = []
  link_list = None

  if "qkxsy" in url:
    link_list = page.find('ul', {'class': 'dirlist'}).findAll('li')
  else:
    link_list = page.find('dl', {'class': 'chapterlist'}).findAll('dd') #stu.la

  for row in link_list:
    a = row.find('a', href=True)

    if a == None:
      continue

    link_suffix = a.attrs['href'] #Looks like /book/51514/8307322.html

    if a.attrs['href'] == '#':
      continue

    link_suffix = link_suffix.strip("/")
    links.append(homepage + link_suffix)
  
  return links

def get_book_title(url):
  page = get_beautiful_soup_html(url)
  h1 = None

  if "qkxsy" in url:
    h1 = page.find('h2').text.strip(' 章節列表')
  else:
    h1 = page.find('h1').text.strip()

  return h1

def div_with_content(div):
  return len(div.findAll('p')) > 0

def get_beautiful_soup_html(url):
  time.sleep(random.random() * 5 + 1.0)
  user_agent = proxy.get_headers()
  response = requests.get(url, headers=user_agent)

  if "qkxsy" in url:
    response.encoding = "UTF-8"
  else:
    response.encoding = "big5"

  return BeautifulSoup(response.text, 'html.parser')

if __name__ == "__main__":
# NOTE: The first command-line arg is the link to the chapter list directly
#   example command python3 get_books_for_mom_stu.py http://www.stu.la/book/51514/ http://www.stu.la/ 0
#   example command python3 get_books_for_mom_stu.py https://www.qkxsy.com/content/116868/ https://www.qkxsy.com/ 0
  book_index_link = sys.argv[1]
  homepage = sys.argv[2]
  start_from = int(sys.argv[3])

  if not homepage in HOMEPAGES:
    print("This script only works for {}! exiting....".format(HOMEPAGES))
    sys.exit(1)

  title = get_book_title(book_index_link)
  print(title)
  print(os.path)

  # Make a directory for the book
  OUTPUT_DIRECTORY = os.path.join("./", title)
  os.mkdir(OUTPUT_DIRECTORY)

  links_to_chapters = get_links_to_chapters(book_index_link, homepage)

  print('links to chapters={}'.format(links_to_chapters))
  links_with_index = []
  for i in range(start_from, len(links_to_chapters)):
    links_with_index.append(links_to_chapters[i] + CUSTOM_DELIMITER + str(i) + " - " + CUSTOM_DELIMITER + title)

  # Download all the chapters in parallel batches	
  pool = Pool(DOWNLOAD_BATCH_SIZE)
  pool.map(parse_and_save_as_text, links_with_index)
  pool.close()
  pool.join()