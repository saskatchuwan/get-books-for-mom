from retrying import retry
from bs4 import BeautifulSoup
from newspaper import Article
from multiprocessing import Pool

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
	article = Article(url, language='zh')
	article.download()
	article.parse()

	index_prefix = index.zfill(8)
	filename = index_prefix + article.title + ".txt"
	file_path = os.path.join(OUTPUT_DIRECTORY, filename)

	# Extract content
	content_soup = BeautifulSoup(article.html, 'html.parser')
	all_divs = content_soup.findAll('div')
	with open(file_path, 'w') as f:
		for div in all_divs:
			if div_with_content(div):
				f.write(div.text)
	print("Downloading {} COMPLETE!".format(filename))

def div_with_content(div):
	return len(div.findAll('p')) > 0

def get_beautiful_soup_html(url):
	time.sleep(random.random() * 5 + 1.0)
	user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
	response = requests.get(url, headers={'User-Agent': user_agent})
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
		link_suffix = a.attrs['href'] #Looks like /zhsbook/43070.html		
		link_suffix = link_suffix.strip("/")
		links.append(HOMEPAGE + link_suffix)
	return links

if __name__ == "__main__":
	# example command python get_books_for_mom.py http://tw.zhsxs.com/zhsbook/29885.html
	book_index_link = sys.argv[1]
	start_from = int(sys.argv[2])
	if not HOMEPAGE in book_index_link:
		print("This script only works for {}! exiting....".format(HOMEPAGE))
		sys.exit(1)

	title = get_book_title(book_index_link)
	print('got title={}'.format(title))
	
	# Make a directory for the book
	OUTPUT_DIRECTORY = os.path.join("./", title)
	os.mkdir(OUTPUT_DIRECTORY)

	links_to_chapters = get_links_to_chapters(book_index_link)
	print('links to chapters={}'.format(links_to_chapters))
	links_with_index = []
	for i in range(start_from, len(links_to_chapters)):
		links_with_index.append(links_to_chapters[i] + CUSTOM_DELIMITER + str(i))

	# Download all the chapters in parallel batches	
	pool = Pool(DOWNLOAD_BATCH_SIZE)
	pool.map(parse_and_save_as_txt, links_with_index)
	pool.close()
	pool.join()
