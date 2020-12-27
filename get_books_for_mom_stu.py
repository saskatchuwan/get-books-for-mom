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

HOMEPAGES = ['http://www.stu.la/']
DOWNLOAD_BATCH_SIZE = 1
CUSTOM_DELIMITER = "$$"

# This value gets changed and the only reason why it's global is because 
# Pythons multiprocessing pool doesn't support multiple arguments
OUTPUT_DIRECTORY = "./"

@retry(stop_max_attempt_number=3, wait_random_min=2000, wait_random_max=4000)
def parse_and_save_as_text(url_with_index):
	# Wait for any time between 1 and 2 seconds.
  time.sleep(1.0 + random.random())	

  url, index = url_with_index.split(CUSTOM_DELIMITER)

  # REQUEST
  article = get_beautiful_soup_html(url)

  # Create output filename
  article_title = article.find('h1').text.strip()

  index_prefix = index.zfill(8) #pad leading zeros until length of 8
  filename = index_prefix + article_title + ".txt"
  file_path = os.path.join(OUTPUT_DIRECTORY, filename)

  with open(file_path, 'w') as f:
    div_with_content = article.find('div', {'class': 'BookText'})
    f.write(div_with_content.text)

  print("Downloading {} COMPLETE!".format(filename))

def get_links_to_chapters(url, homepage):
  page = get_beautiful_soup_html(url)

  links = []
  link_list = page.findAll('dl', {'class': 'chapterlist'})

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

  try:
    if "stu.la" in url:
      h1 = page.find('div', {'class': 'btitle'})

  except:
    h1 = page.find('h1')

  return h1.text.strip()

def div_with_content(div):
  return len(div.findAll('p')) > 0

def get_beautiful_soup_html(url):
  time.sleep(random.random() * 5 + 1.0)
  user_agent = proxy.get_headers()
  response = requests.get(url, headers=user_agent)
  return BeautifulSoup(response.text, 'html.parser')

if __name__ == "__main__":
#   example command python3 get_books_for_mom_stu.py http://www.stu.la/book/51514/ http://www.stu.la/ 0
  book_index_link = sys.argv[1]
  homepage = sys.argv[2]
  start_from = int(sys.argv[3])

  if not homepage in HOMEPAGES:
    print("This script only works for {}! exiting....".format(HOMEPAGES))
    sys.exit(1)

  title = get_book_title(book_index_link)

  # Make a directory for the book
  OUTPUT_DIRECTORY = os.path.join("./", title)
  os.mkdir(OUTPUT_DIRECTORY)

  links_to_chapters = get_links_to_chapters(book_index_link, homepage)

  print('links to chapters={}'.format(links_to_chapters))
  links_with_index = []
  for i in range(start_from, len(links_to_chapters)):
    links_with_index.append(links_to_chapters[i] + CUSTOM_DELIMITER + str(i) + " - ")

  # Download all the chapters in parallel batches	
  pool = Pool(DOWNLOAD_BATCH_SIZE)
  pool.map(parse_and_save_as_text, links_with_index)
  pool.close()
  pool.join()