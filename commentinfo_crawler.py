
# coding: utf-8

# In[ ]:

import sys
# novel_id = '8161510403317103'
novel_id = sys.argv[1]


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


CommentInfo = namedtuple('CommentInfo', ['author_name', 'author_id', 'post_id', 'content'])


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


def get_comment_info(comment_obj, post_id):
    post_author_obj = comment_obj.find('p', class_='auther')
    post_author_name = post_author_obj.a.get_text()
    post_author_id = get_id_from_url(post_author_obj.a['href'])
    content = comment_obj.find('p', class_='post-body').get_text().strip().replace('\n', ' ')
    return CommentInfo(author_name=post_author_name, author_id=post_author_id, post_id=post_id, content=content)


# In[ ]:


def comment_info_func_with_postid(post_id):
    return lambda x: get_comment_info(x, post_id)


# In[ ]:


def get_comments_on_page(novel_id, post_id, page_id):
    URL = "https://forum.qidian.com/post/%s/%s?page=%d" % (novel_id, post_id, page_id)
    comments_obj = get_bsObj(URL)
    comment_objs = comments_obj.findAll('div', class_='post-hover')
    comment_infos = map(comment_info_func_with_postid(post_id), comment_objs)
    return list(comment_infos)


# In[ ]:


start = start_batch = time.time()
comment_num = 0
with open('data/%s/PostInfo-%s.csv' % (novel_id, novel_id), 'r') as f, open('data/%s/CommentInfo-%s.csv' % (novel_id, novel_id), 'w+') as g:
    for post_index, line in enumerate(f, 1):
        comments_list = []
        post_author_name, post_author_id, post_id = line.strip().split(', ')
        page_num = 0
        while True:
            comments = get_comments_on_page(novel_id, post_id, page_num + 1)
            if comments:
                comments_list.extend(comments)
                page_num += 1
            else:
                break
        for info in comments_list:
            print(info.author_name, info.author_id, info.post_id, info.content, sep=', ', file=g)
        comment_num += len(comments_list)
        
        if post_index % 10 == 0:
            print('Has read comments of %d posts' % post_index)
            print('Use %.6fs during these 10 posts...' % (time.time()-start_batch))
            start_batch = time.time()

print('The novel has %d comments!' % comment_num)

