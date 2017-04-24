'''
Created on 2017年3月17日

@author: 
'''
from bs4 import BeautifulSoup
import re
import chardet

def get_root_url(url):
    bls = url.split(sep='/')
    return bls[0]+'/'+bls[1]+'/'+bls[2]

class HtmlParser(object):


    def _get_new_urls(self, page_url, soup):
        new_urls = set()
        
        
        
        root_url = get_root_url(page_url)
        links = soup.find_all('a',href=re.compile(root_url+r'/.*'))
        for link in links:
            new_url = link['href']
            if get_root_url(new_url) == root_url:
                new_urls.add(new_url)
        return new_urls    
        
    def _get_new_data(self, page_url, soup):
        return soup.get_text()
    
    
    def parse(self,page_url,html_cont):
        if page_url is None or html_cont is None:
            return 
        soup = BeautifulSoup(html_cont,'html.parser')
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls,new_data
