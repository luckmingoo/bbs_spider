#coding:utf-8
'''
Created on 2017年3月17日

@author:mingo
'''
import url_manager, html_downloader, html_parser, html_outputer
import chardet
import os
import re
import hashlib
import redis


def filter_tags(htmlstr):
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I)
    re_script=re.compile('<\s*script[^>]*>[\s\S]*?<\s*/\s*script\s*>',re.I)
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)
    re_comment=re.compile('<!--[\s\S]*?-->')
    s=re_cdata.sub('',htmlstr)
    s=re_script.sub('',s)
    s=re_style.sub('',s)
    s=re_comment.sub('',s)
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)
    return s

def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}
    
    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()
        key=sz.group('name')
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)

class SpiderMain(object):
    def __init__(self,lib_name,count):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()
        self.name = lib_name
        self.charset = ''
        self.count = count
    
    def get_data(self, url):
        count = 1
        root_url = get_root_url(url)
        self.urls.add_assist_url(root_url)
        if url.find('&extra') != -1:
            url = url[0:url.find('&extra')]
        if url.find('&page') != -1:
            url = url[0:url.find('&page')]
        p1 = get_re(url)  # 获取正则表达式
        pa_url = re.compile(p1)
        while self.urls.has_assist_url():
            try:
                new_url = self.urls.get_assist_url()
                print('craw %d : %s' % (count,new_url))
                
                html_cont =self.downloader.download(new_url)
                if html_cont is None:
                    continue
                mychar = chardet.detect(html_cont[:500])
                html_cont = html_cont.decode(mychar['encoding'],'ignore')
                html_cont = filter_tags(html_cont)
                #html_cont为带标签的html
                new_urls,new_data = self.parser.parse(new_url,html_cont)  
                #分为满足要求得url和不满足要求得url
                main_urls = set()
                assist_urls = set()
                for a_url in new_urls:
                    if a_url.find('&extra') != -1:
                        a_url = a_url[0:a_url.find('&extra')]
                    if a_url.find('&page') != -1:
                        a_url = a_url[0:a_url.find('&page')]
                    if pa_url.match(a_url):
                        main_urls.add(a_url)
                        #print(a_url)
                    else:
                        assist_urls.add(a_url)
                self.urls.add_assist_urls(assist_urls)
                self.urls.add_main_urls(main_urls)
                while self.urls.has_main_url():
                    main_url = self.urls.get_main_url()
                    print('craw %d : %s' % (count,main_url))
                    main_html_cont =self.downloader.download(main_url)
                    main_mychar = chardet.detect(main_html_cont[:500])
                    main_html_cont = main_html_cont.decode(main_mychar['encoding'],'ignore')
                    main_html_cont = filter_tags(main_html_cont)
                    #html_cont为带标签的html
                    new_urls,new_data = self.parser.parse(new_url,html_cont)  
                    #分为满足要求得url和不满足要求得url
                    main_urls = set()
                    assist_urls = set()
                    for a_url in new_urls:
                        if a_url.find('&extra') != -1:
                            a_url = a_url[0:a_url.find('&extra')]
                        if a_url.find('&page') != -1:
                            a_url = a_url[0:a_url.find('&page')]
                        if pa_url.match(a_url):
                            main_urls.add(a_url)
                            #print(a_url)
                        else:
                            assist_urls.add(a_url)
                    self.urls.add_assist_urls(assist_urls)
                    self.urls.add_main_urls(main_urls)
                    pattern = re.compile(">[\s\S]*?<",re.I)
                    ret = re.findall(pattern,main_html_cont) #ret为得到的标签之间的内容
                    for li in ret:
                        li = li[1:-1].strip()
                        if li:
                            #排除在引号中出现">"的情况
                            punc = re.compile('"')
                            if len(punc.findall(li))%2:
                                continue
                            m = hashlib.md5(li.encode("utf-8")).hexdigest()
                            r.hincrby(self.name,m,amount=1)  #以域名建立数据库
                
                    if count == 10 :
                        break
                    count += 1
                if count == 10:
                    break
            except:
                print('craw failed')

    
    def craw(self, url):
        html_cont =self.downloader.download(url)
        if html_cont is None or not html_cont:
            return None
        try:
            mychar = chardet.detect(html_cont[:500])
            html_cont = html_cont.decode(mychar['encoding'],'ignore')
            self.charset = mychar['encoding']
        except:
            return None
        html_cont = filter_tags(html_cont)
        cont = ''
        lastline = ''
        currline = ''
        lines = html_cont.splitlines()
        for line in lines:
            currline = line.strip()
            if not lastline:
                lastline = currline
            if currline :
                if currline[0] == '<':
                    if lastline[-1] == '>':
                        pattern = re.compile(">[\s\S]*?<",re.I)
                        ret = re.findall(pattern,lastline) #ret为得到的标签之间的内容
                        for li in ret:
                            li = li[1:-1].strip()
                            if not li:
                                continue
                            #排除在引号中出现">"的情况
                            punc = re.compile('"')
                            if len(punc.findall(li))%2:
                                continue
                            m = hashlib.md5(li.encode("utf-8")).hexdigest()
                            if r.hexists(self.name,m):
                                if int(r.hget(self.name,m)) >= 2:       #有2次以上的重复记录，则删除，需要优化
                                    lastline = lastline.replace(li, '')
                        cont += lastline + '\n'
                        lastline = currline
                    else:
                        lastline += currline    
                else:
                    lastline += currline
        url=url.replace('/','+')
        url=url.replace(':','~')
        url=url.replace('?','^')
        fp = open("out/" + url,'wb')
        fp.write(cont.encode('utf-8'))
        fp.close()

    
    
    
def get_root_url(url):
    bls = url.split(sep='/')
    return bls[0]+'/'+bls[1]+'/'+bls[2]

def get_lib_name(url):
    bls = url.split(sep='/')
    return bls[2]

def get_re(url):
    url = url[7:]  # 去除http://
    Len = len(url)
    p = "http://"
    i = 0
    while i < Len:
        if url[i] == '.':
            p += '.'
        elif 'a' <= url[i] <= 'z':  # 不能直接判isplpha，因为str[i]中全都是字符
            p += '[a-z]'
        elif 'A' <= url[i] <= 'Z':
            p += '[A-Z]'
        elif '0' <= url[i] <= '9':
            p += '\d'
        else:
            p += url[i]
        i += 1
    return p


if __name__ == "__main__":
    count = 1
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    r = redis.Redis(connection_pool=pool)
    #r.flushdb()     #清空之前的数据
    fp1 = open('new_urls.txt','r')
    cont = fp1.read()
    fp1.close()
    urls = cont.splitlines()
    for url in urls:
        if not url:
            continue
        obj_spider = SpiderMain(get_lib_name(url),count)
        if r.exists(obj_spider.name):
            pass
        else:
            obj_spider.get_data(url)
        obj_spider.craw(url)
        print('%d:%s'%(count,url))
        count +=1
    print('over')
    