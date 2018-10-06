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

def parse_author_id(text):
    return text.split('/')[-1]

if __name__ == '__main__':

    novel_ids = [9717820404859503]

    for novel_id in novel_ids:

        thread_prefix = '//forum.qidian.com/post/%d' % novel_id

        nodes, edges = set(), dict()

        thread_page = 0
        thread_num = 0

        while True:

            thread_page += 1
            novel_entry = get_bsObj('https://forum.qidian.com/index/%d?type=1&page=%d' % (novel_id, thread_page))
            threads = novel_entry.findAll('a', target='_blank', class_='black', href=re.compile("^%s" % thread_prefix))
            
            if not threads:
                break

            for thread_id in threads:

                thread_num += 1

                if 'href' in thread_id.attrs:

                    comment_page = 0

                    while True:

                        comment_page += 1
                        thread = get_bsObj('https:' + thread_id.attrs['href'] + '?page=%d' % comment_page)
                        main_body = thread.find('div', class_='main-body fl')

                        if comment_page == 1:
                            thread_author = main_body.find('div', class_='post-wrap cf').find('p', class_='auther').a
                            thread_author_name = thread_author.get_text()
                            thread_author_id = parse_author_id(thread_author['href'])
                            nodes.add(thread_author_id)
                            # print(' Thread Author:', thread_author_name, thread_author_id)

                        comments = main_body.findAll('li', class_='comment-wrap cf')
                        if not comments:
                            break
                        for comment in comments:
                            comment_author = comment.find('div', class_='post').find('p', 'auther').a
                            comment_author_name = comment_author.get_text()
                            comment_author_id = parse_author_id(comment_author['href'])

                            nodes.add(comment_author_id)
                            edges[(comment_author_id, thread_author_id)] = \
                            edges.get((comment_author_id, thread_author_id), 0) + 1
                            # print('Comment Author:', comment_author_name, comment_author_id)

                        
                    # print('The thread has %d page(s) of comment(s)' % (comment_page - 1))

                print('Crawling the %d-th thread Finish!' % (thread_num))

        print('Crawling Novel %s Finish!' % (novel_name))
        print(len(nodes), len(edges))
