from urllib.request import urlopen
from bs4 import BeautifulSoup as BS

import requests
import re

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

def get_bsObj(url):
    try:
        req = session.get(url, headers=headers)
    except HTTPError as e:
        return None

    try:
        bsObj = BS(req.text, "lxml")
    except AttributeError as e:
        return None
    return bsObj

def get_post_entry(novel_id, page_num, url_body='https://forum.qidian.com/index/%s?type=1&page=%d'):
    real_url = url_body % (novel_id, page_num)
    return get_bsObj(real_url)

def get_comment_entry(post_id, page_num, url_body='https:%s?page=%d'):
    real_url = url_body % (post_id, page_num)
    return get_bsObj(real_url)

def parse_author_id(text):
    return text.split('/')[-1]

def write_weights(weights, novel_id, filename=None):
    cleaned_weights = [
        '%s, %s, %d, %d' % (e[0].user_id, e[1].user_id, w.count, w.len_sum)
        for e, w in weights.items()
    ]
    if filename is None:
        filename = '%s.csv' % novel_id
    with open(filename, 'w+') as f:
        for w in cleaned_weights:
            print(w, file=f)