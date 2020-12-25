#!/usr/bin/env python
# coding: utf-8

# In[1]:


from collections import defaultdict
import os
import requests
import time

from bs4 import BeautifulSoup as BS
import simplejson as json
from tenacity import retry, stop_after_attempt, wait_random
from wos import WosClient
import wos.utils


# In[2]:


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


# In[3]:


os.makedirs('data/author_to_articles',exist_ok=True)


# In[4]:


import glob

article_infos = []
uidlist = glob.glob('data/uid_to_article/*.json')

for uid_n, uid in enumerate(uidlist, 1):
    if uid_n % 1000 == 0:
        print(f'Reading Article ID = {uid_n} to Construct Author List')

    with open(uid, 'r') as f:
        article_info = json.load(f)
        article_infos.append(article_info)


# In[5]:


authors = list()
author_ids = set()
for article_info in article_infos:
    for author_name, author_id in zip(article_info['author_name'], article_info['author_id']):
        if author_id not in author_ids:
            author_ids.add(author_id)
            authors.append((author_name, author_id))
authors = sorted(set(authors))
print(f'There Are {len(authors)} Different Authors.')


# In[6]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_bsObj(url):
    try:
        req = session.get(url, headers=headers)
    except HTTPError:
        return None

    try:
        bsObj = BS(req.text, "html.parser")
    except AttributeError:
        return None
    return bsObj


# In[7]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_sum_with_uid(article_uid, client):
    article_bs = BS(client.retrieveById(article_uid).records, 'html.parser')
    summary = article_bs.find('summary')
    return extract_metadata_from_summary(summary)


# In[8]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_refs_with_uid(article_uid, client):
    
    refs = client.citedReferences(article_uid)
    refQueryId, refRecordsFound = refs.queryId, refs.recordsFound

    ref_meta_list = []
    for j in range(1, refRecordsFound+1, 100):
        if j != 1:
            time.sleep(2)
        ref_r = wc.citedReferencesRetrieve(refQueryId, count=min(100, refRecordsFound+1-j), offset=j)
        ref_meta_list.extend([dict(ref) for ref in ref_r])
    return ref_meta_list


# In[9]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_inv_refs_with_uid(article_uid, client):
    cits = wc.citingArticles(article_uid)
    citRecordsFound = cits.recordsFound
    
    inv_ref_meta_list = []
    for j in range(1, citRecordsFound+1, 100):
        if j != 1:
            time.sleep(2)
        inv_refs = wc.citingArticles(article_uid, count=min(100, citRecordsFound+1-j), offset=j)
        inv_refs = BS(inv_refs.records, 'html.parser')
        inv_ref_summaries = inv_refs.findAll('summary')
        inv_ref_meta_list.extend([extract_metadata_from_summary(inv_ref_summary) for inv_ref_summary in inv_ref_summaries])
    return inv_ref_meta_list


# In[10]:


def extract_metadata_from_summary(summary):
#     print(summary.find('title', type='item').text)
    return {
        'title': summary.find('title', type='item').text,
        'author_name': [author.text for author in summary.findAll('wos_standard')],
        'author_id': [author.get('daisng_id') for author in summary.findAll('name', role='author')],
        'pubyear': summary.find('pub_info')['pubyear']
    }


# In[11]:


import re

crawled_authors = glob.glob('data/author_to_articles/*.json')
crawled_authors = set([os.path.basename(filename).split('.')[0] for filename in crawled_authors])
print(f'There Are {len(crawled_authors)} Collected Authors. Remain {len(authors) - len(crawled_authors)} Authors.')
remained_authors = [author for author in authors if author[1] not in crawled_authors][::-1]

wc = WosClient()
wc.connect()
for author_order, (author_name, author_id) in enumerate(remained_authors, 1):
    
    print(f'Finding Articles of Author {author_order}: {author_name} ({author_id})')
    if author_order % 100 == 0:
        wc.close()
        wc = WosClient()
        wc.connect()

    query_url = "https://apps.webofknowledge.com/" +     f"InboundService.do?product=WOS&daisIds={author_id}" +     "&Func=Frame&DestFail=http%3A%2F%2Fwww.webofknowledge.com" +     f"&SrcApp=RRC&locale=zh_TW&SrcAuth=RRCPubList&SID={wc._SID}" +     "&customersID=RRCPubList&mode=SourceByDais&IsProductCode=Yes&Init=Yes&viewType=summary&action=search" +     "&action=changePageSize&pageSize=50"
    wos_codes = []
    
    while True:

        bsObj = get_bsObj(query_url)
        articles = bsObj.findAll('div', id=re.compile('^RECORD_[0-9]+$'))
        for article in articles:
            wos_url = article.find('div', class_='search-results-content').find('span', {'style': 'display: none'})['url']
            wos_code = [part for part in wos_url.split('&') if 'isickref=' in part]
            wos_code = wos_code[0].split('=')[1]
            wos_codes.append(wos_code)
#             print(wos_code)

        next_page_button = bsObj.find('a', class_='paginationNext snowplow-navigation-nextpage-top')
        if next_page_button is None:
            break
        
        next_page_url = next_page_button['href']
        query_url = next_page_url
    
    print(f'{len(wos_codes)} Articles Found.')
    
    
    with open(f'data/author_to_articles/{author_id}.json', 'w') as f:
        dump_data = {
            'author_id': author_id,
            'author_name': author_name,
            'uids': wos_codes
        }
        json.dump(dump_data, f, indent=4)

wc.close()

