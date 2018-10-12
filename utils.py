from bs4 import BeautifulSoup as BS
from urllib.error import HTTPError

import requests

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
    except HTTPError:
        return None

    try:
        bsObj = BS(req.text, "lxml")
    except AttributeError:
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

def parse_author_name(name_string):
    ranks = ['舵主', '堂主', '护法', '长老', '掌门', '宗师', '盟主', '本书作者']
    parsed_name = name_string.split()
    assert len(parsed_name) <= 2
    
    if len(parsed_name) == 2:
        rank, name = parsed_name
        rank = rank[1:-1]
        assert rank in ranks
        return name, rank
    else:
        return parsed_name[0], '無'

def write_weights_of_novel(novel, file_prefix=None, mode='w+'):
    weights = novel.calculate()
    novel_id = novel.novel_id
    
    cleaned_weights = [
        (e[0].user_id, e[1].user_id, w.count, w.len_sum)
        for e, w in weights.items()
    ]
    cleaned_weights.sort()
    
    if filename is None:
        filename = '%s_edge.csv' % novel_id
    with open(filename, mode) as f:
        print('Source, Target, Type, Weight1, Weight2', file=f)
        for w in cleaned_weights:
            print(', '.join([w[0], w[1], 'Directed', str(w[2]), str(w[3])]), file=f)

def write_users_of_novel(novel, file_prefix=None, mode='w+'):
    users = novel.involved_users
    novel_id = novel.novel_id
    
    if filename is None:
        filename = '%s_node.csv' % novel_id
    with open(filename, mode) as f:
        print('Id, Label, Attribute', file=f)
        for user in users:
            print(', '.join([user.user_id, user.name, str(user.rank)]), file=f)