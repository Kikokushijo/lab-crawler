from selenium import webdriver
from bs4 import BeautifulSoup as BS
import re, time

driver = webdriver.PhantomJS(executable_path='../../phantomjs-2.1.1-linux-x86_64/bin/phantomjs')


with open('list.csv', 'r') as f, open('index_list.txt', 'w+') as g:
    for line in f:
        _, name, genre, _, url, *_ = line.strip().split(',')
        print(name, genre, url)
        driver.get(url)
        time.sleep(5)
        page_source = driver.page_source
        bsObj = BS(page_source)
        real_url = bsObj.find(
            'a', 
            class_='lang', 
            href=re.compile('^//forum.qidian.com/index/'), 
            target='_blank'
        )['href']
        real_url = 'https:' + real_url
        # print(name, genre, url, real_url)
        print(real_url.split('/')[-1], file=g)