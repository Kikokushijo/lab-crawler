#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from collections import defaultdict
import os
import time
import sys

from bs4 import BeautifulSoup as BS
import simplejson as json
from tenacity import retry, stop_after_attempt, wait_random
from wos import WosClient
import wos.utils


# In[ ]:


os.makedirs('data/universe/uid_to_article',exist_ok=True)
os.makedirs('data/universe/uid_to_refs',exist_ok=True)
os.makedirs('data/universe/uid_to_inv_refs',exist_ok=True)


# In[ ]:


# import glob

# article_infos = []
# article_ids = glob.glob('data/author_to_articles/*.json')

# author_to_articles = []
# for id_n, article_id in enumerate(article_ids, 1):
#     if id_n % 1000 == 0:
#         print(f'Reading Article ID = {id_n} to Construct Article List')

#     with open(article_id, 'r') as f:
#         author_info = json.load(f)
#         author_to_articles.append(author_info)


# In[ ]:


# with open('all_article_uids.json', 'w+') as f:
#     json.dump(all_uids, f)

with open('all_article_uids.json', 'r') as f:
    all_uids = json.load(f)


# In[ ]:


# all_uids = set()
# for d in author_to_articles:
#     all_uids.update(d['uids'])
# all_uids = sorted(all_uids)
print(f'There Are {len(all_uids)} Articles.')


# In[ ]:


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


# In[ ]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_sum_with_uid(article_uid, client):
    article_bs = BS(client.retrieveById(article_uid).records, 'html.parser')
    summary = article_bs.find('summary')
    return extract_metadata_from_summary(summary)


# In[ ]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_refs_with_uid(article_uid, client):
    
    refs = client.citedReferences(article_uid)
    refQueryId, refRecordsFound = refs.queryId, refs.recordsFound

    ref_meta_list = []
    for j in range(1, refRecordsFound+1, 100):
#         if j != 1:
#             time.sleep(2)
        ref_r = client.citedReferencesRetrieve(refQueryId, count=min(100, refRecordsFound+1-j), offset=j)
        ref_meta_list.extend([dict(ref) for ref in ref_r])
    return ref_meta_list


# In[ ]:


@retry(stop=stop_after_attempt(3), 
       wait=wait_random(min=1, max=2))
def get_inv_refs_with_uid(article_uid, client):
    cits = client.citingArticles(article_uid)
    citRecordsFound = cits.recordsFound
    
    inv_ref_meta_list = []
    for j in range(1, citRecordsFound+1, 100):
#         if j != 1:
#             time.sleep(2)
        inv_refs = client.citingArticles(article_uid, count=min(100, citRecordsFound+1-j), offset=j)
        inv_refs = BS(inv_refs.records, 'html.parser')
        inv_ref_summaries = inv_refs.findAll('summary')
        inv_ref_meta_list.extend([extract_metadata_from_summary(inv_ref_summary) for inv_ref_summary in inv_ref_summaries])
    return inv_ref_meta_list


# In[ ]:


def extract_metadata_from_summary(summary):
#     print(summary.find('title', type='item').text)
    return {
        'title': summary.find('title', type='item').text,
        'author_name': [author.text for author in summary.findAll('wos_standard')],
        'author_id': [author.get('daisng_id') for author in summary.findAll('name', role='author')],
        'pubyear': summary.find('pub_info')['pubyear']
    }


# In[ ]:


# total_batch, nth_batch = 8, 0
total_batch, nth_batch = int(sys.argv[1]), int(sys.argv[2])
print(f'Now batch querying {nth_batch} of total {total_batch} batches')
batch_size = len(all_uids) // total_batch
batch_uids = all_uids[batch_size*nth_batch:batch_size*(nth_batch+1)]


# In[ ]:


summary_client = WosClient()
refs_client = WosClient()
inv_refs_client = WosClient()
summary_client.connect()
refs_client.connect()
inv_refs_client.connect()

start_time = time.time()
for idx, wos_code in enumerate(batch_uids, 1):
    
    if idx % 150 == 0:
        print(f'Has downloaded info of {idx} articles, Time elapsed: {time.time() - start_time: .4f}')
        start_time = time.time()
        
        # close original clients
        summary_client.close()
        refs_client.close()
        inv_refs_client.close()
        
        # init new clients
        summary_client = WosClient()
        refs_client = WosClient()
        inv_refs_client = WosClient()
        summary_client.connect()
        refs_client.connect()
        inv_refs_client.connect()
        
    
    digit_part = wos_code[4:]
    summary_filename = os.path.join('data/universe/uid_to_article', f'{digit_part}.json')
    refs_filename = os.path.join('data/universe/uid_to_refs', f'{digit_part}.json')
    inv_refs_filename = os.path.join('data/universe/uid_to_inv_refs', f'{digit_part}.json')
    all_filename = [summary_filename, refs_filename, inv_refs_filename]
                    
    if all(os.path.exists(filename) for filename in all_filename):
        continue
    
    summary  = get_sum_with_uid(wos_code, summary_client)
    with open(summary_filename, 'w+') as f:
        json.dump(summary, f)
    
    refs     = get_refs_with_uid(wos_code, refs_client)
    with open(refs_filename, 'w+') as f:
        json.dump(refs, f)
        
    inv_refs = get_inv_refs_with_uid(wos_code, inv_refs_client)
    with open(inv_refs_filename, 'w+') as f:
        json.dump(inv_refs, f)
        
summary_client.close()
refs_client.close()
inv_refs_client.close()


# In[ ]:




