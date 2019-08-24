import random
import requests
from bs4 import BeautifulSoup
import user_agents


def get_headers():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "User-Agent": get_random_user_agent()
    }

    return headers

def get_proxies():
    proxies = get_list_of_proxies()
    random_proxy = random.sample(proxies, 1)[0]
    proxy_dict = { 
              "http"  : "http://"+random_proxy, 
              "https" : "https://"+random_proxy
            }
    return proxy_dict

def get_list_of_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = BeautifulSoup(response.text, "html.parser")
    proxies = set()

    ip_table = parser.find('table', {'id': 'proxylisttable'}).find('tbody')
    ip_sections = ip_table.findAll('tr')
    
    for section in ip_sections:
        ip = section.findAll('td')[0].text
        port = section.findAll('td')[1].text

        proxy = ip + ':' + port
        proxies.add(proxy)
    
    return proxies

def get_random_user_agent():
    return random.choice(user_agents.useragents)


if __name__ == "__main__":
    print(get_proxies())