'''
Created on 2017年3月17日

@author: 
'''
import urllib.request


class HtmlDownloader(object):

    def download(self,url):
        if url is None:
            return None
        
        try:
            head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
            req = urllib.request.Request(url, headers=head)
            response = urllib.request.urlopen(req,timeout=3)

            if response.getcode() != 200:
                return None
            return response.read()
        except :#urllib.error.HTTPError as e:
            return None