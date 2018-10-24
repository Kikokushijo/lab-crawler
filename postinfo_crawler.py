
# coding: utf-8

# In[ ]:

import sys, pathlib

# novel_id = '8161510403317103'
novel_id = sys.argv[1]
pathlib.Path('data/%s' % novel_id).mkdir(parents=True, exist_ok=True) 

# In[ ]:


from bs4 import BeautifulSoup as BS
from urllib.error import HTTPError
import requests, re
from collections import namedtuple
from multiprocessing import Pool
import time


# In[ ]:


session = requests.Session()
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com.tw/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "\
                  "Chrome/69.0.3497.92 Safari/537.36"
}


# In[ ]:


PostInfo = namedtuple('PostInfo', ['author_name', 'author_id', 'post_id'])


# In[ ]:


def get_bsObj(url):
    try:
        req = session.get(url, headers=headers)
    except HTTPError:
        return None

    try:
        bsObj = BS(req.text, "lxml")
    except AttributeError:
        return None
    return bsObj


# In[ ]:


def get_id_from_url(url):
    return url.split('/')[-1]


# In[ ]:


def get_post_info(post_obj):
    post_prefix = '//forum.qidian.com/post/'
    author_obj = post_obj.find('p', class_='post-auther').find('a')
    author_name = author_obj.get_text()
    author_id = get_id_from_url(author_obj['href'])
    post_entry_obj = post_obj.find('p', class_=re.compile('^post\-(?!auther)')).find('a', target='_blank')
    post_id = get_id_from_url(post_entry_obj['href'])
    return PostInfo(author_name=author_name, author_id=author_id, post_id=post_id)


# In[ ]:


def get_posts_on_page(novel_id, page_id):
    URL = "https://forum.qidian.com/index/%s?type=1&page=%d" % (novel_id, page_id)
    posts_obj = get_bsObj(URL)
    post_objs = posts_obj.findAll('div', class_='post')
    post_infos = map(get_post_info, post_objs)
    return list(post_infos)


# In[ ]:


start = start_batch = time.time()
posts_list = []
page_num = 0
while True:
    posts = get_posts_on_page(novel_id, page_num + 1)
    if posts:
        posts_list.extend(posts)
        page_num += 1
    else:
        break
    
    if page_num % 10 == 0:
        print('Has read %d pages of post entries...' % page_num)
        print('Use %.6fs during these 10 pages...' % (time.time()-start_batch))
        start_batch = time.time()
print('The novel has %d page(s) of (or %d) posts!' % (page_num, len(posts_list)))


# In[ ]:


with open('data/%s/PostInfo-%s.csv' % (novel_id, novel_id), 'w+') as f:
    for info in posts_list:
        print(info.author_name, info.author_id, info.post_id, sep=', ', file=f)

