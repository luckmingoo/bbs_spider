'''
Created on 2017年3月17日

@author: 
'''
import os


class HtmlOutputer(object):
    def __init__(self):
        self.datas = ''
        
    def collect_data(self,data):
        if data is None:
            return
        self.datas += data

    
    def output_html(self):
        fout = open('output.txt','wb')
        fout.write(self.datas.encode('utf-8'))
        fout.close()
    
    

