from multiprocessing import Pool
from retrying import retry

import random
import os
import time
import sys

import scraper

HOMEPAGES = ['http://tw.zhsxs.com/', 'https://tw.bsxsw.com/', 'http://tw.mingzw.net/']
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
  article = scraper.get_beautiful_soup_html(url)

  article_title = None
  book_directory = None

  # Create output filename
  if "tw.mingzw.net" in url:
    title = article.find('div', {'class': 'novel-top2'}).find(text=True, recursive=False).strip()
    title = title.split('-')

    article_title = title[1]
    book_directory = title[0]
  else:
    article_title = article.find('h1').text.strip()
    # book_directory = article.find('title').text.split('_')[0] #this broke.
    book_directory = "問丹朱" # TODO: need some reference to the title of the book here, but for now, just hardcode when running script

  index_prefix = index.zfill(8) #pad leading zeros until length of 8
  filename = index_prefix + article_title + ".txt"
  file_path = os.path.join(OUTPUT_DIRECTORY, book_directory, filename)

  with open(file_path, 'w') as f:
    if "tw.bsxsw.com" in url:
      div_with_content = article.find('div', {'class': 'ReadContents'})
      f.write(div_with_content.text)

    if "tw.mingzw.net" in url:
      div_with_content = article.find('div', {'class': 'content'})
      f.write(div_with_content.text)
  
    else:
      all_divs = article.findAll('div')
      for div in all_divs:
        # Look for div containing paragraphs of text of the book
        if scraper.div_with_content(div):
          # When found, write only the text within the <p> tags
          f.write(div.text)

  print("Downloading {} COMPLETE!".format(filename))


if __name__ == "__main__":
  # example command python3 get_books_for_mom.py http://tw.zhsxs.com/zhsbook/37706.html http://tw.zhsxs.com/ zhs 0
  # example command python3 get_books_for_mom.py https://tw.bsxsw.com/bsbook/24244.html https://tw.bsxsw.com/ bs 0
  # example command python3 get_books_for_mom.py http://tw.mingzw.net/mzwbook/27902.html http://tw.mingzw.net/ mzw 0
  book_index_link = sys.argv[1]
  homepage = sys.argv[2]
  prefix = sys.argv[3]
  start_from = int(sys.argv[4])

  if not homepage in HOMEPAGES:
    print("This script only works for {}! exiting....".format(HOMEPAGES))
    sys.exit(1)

  title = scraper.get_book_title(book_index_link)

  # Make a directory for the book
  OUTPUT_DIRECTORY = os.path.join("./", title)
  os.mkdir(OUTPUT_DIRECTORY)

  links_to_chapters = scraper.get_links_to_chapters(book_index_link, prefix, homepage)

  print('links to chapters={}'.format(links_to_chapters))
  links_with_index = []
  for i in range(start_from, len(links_to_chapters)):
    links_with_index.append(links_to_chapters[i] + CUSTOM_DELIMITER + str(i) + " - ")

  # Download all the chapters in parallel batches	
  pool = Pool(DOWNLOAD_BATCH_SIZE)
  pool.map(parse_and_save_as_text, links_with_index)
  pool.close()
  pool.join()