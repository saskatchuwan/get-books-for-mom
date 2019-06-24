from multiprocessing import Pool
from retrying import retry

import random
import os
import time
import sys

import scraper

HOMEPAGE = 'http://tw.zhsxs.com/'
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
  index = int(index) + 318
  index = str(index)

  # REQUEST
  article = scraper.get_beautiful_soup_html(url)

  # Create output filename
  article_title = article.find('h1').text.strip()
  index_prefix = index.zfill(8) #pad leading zeros until length of 8
  filename = index_prefix + article_title + ".txt"
  file_path = os.path.join(OUTPUT_DIRECTORY, filename)

  
  all_divs = article.findAll('div')
  with open(file_path, 'w') as f:
    for div in all_divs:
      # Look for div containing paragraphs of text of the book
      if scraper.div_with_content(div):
        # When found, write only the text within the <p> tags
        f.write(div.text)
  print("Downloading {} COMPLETE!".format(filename))


if __name__ == "__main__":
  # example command python get_books_for_mom.py http://tw.zhsxs.com/zhsbook/29885.html 0
  book_index_link = sys.argv[1]
  start_from = int(sys.argv[2])
  if not HOMEPAGE in book_index_link:
    print("This script only works for {}! exiting....".format(HOMEPAGE))
    sys.exit(1)

  title = scraper.get_book_title(book_index_link)
  print('got title={}'.format(title))

  # Make a directory for the book
  OUTPUT_DIRECTORY = os.path.join("./", title)
  os.mkdir(OUTPUT_DIRECTORY)

  links_to_chapters = scraper.get_links_to_chapters(book_index_link)

  print('links to chapters={}'.format(links_to_chapters))
  links_with_index = []
  for i in range(start_from, len(links_to_chapters)):
    links_with_index.append(links_to_chapters[i] + CUSTOM_DELIMITER + str(i))

  # Download all the chapters in parallel batches	
  pool = Pool(DOWNLOAD_BATCH_SIZE)
  pool.map(parse_and_save_as_text, links_with_index)
  pool.close()
  pool.join()