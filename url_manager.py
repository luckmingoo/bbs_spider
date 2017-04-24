'''
Created on 2017年3月17日

@author: 
'''


class UrlManager(object):
    def __init__(self):
        self.assist_urls = set()
        self.main_urls = set()
        self.old_urls = set()
        
    def add_assist_url(self,url):
        if url is None:
            return
        if url not in self.assist_urls and url not in self.main_urls and url not in self.old_urls:
            self.assist_urls.add(url)

    
    def add_assist_urls(self,urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_assist_url(url)
    
    def add_main_url(self,url):
        if url is None:
            return
        if url not in self.assist_urls and url not in self.main_urls and url not in self.old_urls:
            self.main_urls.add(url)

    
    def add_main_urls(self,urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_main_url(url)
            
    def has_assist_url(self):
        return len(self.assist_urls) != 0

    def has_main_url(self):
        return len(self.main_urls) != 0
    
    def get_assist_url(self):
        new_url = self.assist_urls.pop()
        self.old_urls.add(new_url)
        return new_url
    
    def get_main_url(self):
        new_url = self.main_urls.pop()
        self.old_urls.add(new_url)
        return new_url
    

