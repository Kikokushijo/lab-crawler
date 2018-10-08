from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import requests
import re

import utils
from objects import User, Comment, NovelComments

# settings
novel_ids = ['9717820404859503']


if __name__ == '__main__':

    for novel_id in novel_ids:

        thread_prefix = '//forum.qidian.com/post/%s' % novel_id
        thread_page_num, thread_num = 0, 0
        
        # TODO: parse the author of novel
        novel_network = NovelComments(
            novel_id=novel_id,
            author=None
        )

        while True:

            thread_page_num += 1
            thread_entry = utils.get_thread_entry(
                novel_id=novel_id, 
                page_num=thread_page_num
            )
            thread_objs = thread_entry.findAll(
                'div', class_='post', 
            )

            print('thread obj:', len(thread_objs))

            thread_objs = [
                thread_obj.find(
                    'a', {
                     'target': '_blank',
                     'href': re.compile("^%s" % thread_prefix)
                    }
                ) for thread_obj in thread_objs
            ]
            
            # there is no threads in new page
            if not thread_objs:
                break

            # start reading a thread
            for thread_obj in thread_objs:

                thread_author = None
                thread_num += 1

                assert 'href' in thread_obj.attrs

                comment_page_num = 0
                while True:
                    comment_page_num += 1
                    thread = utils.get_comment_entry(
                        thread_id=thread_obj.attrs['href'], 
                        page_num=comment_page_num
                    )
                    main_body = thread.find(
                        'div', class_='main-body fl'
                    )

                    # there is the author of the thread
                    if comment_page_num == 1:

                        thread_author_obj = main_body.find(
                            'div', class_='post-wrap cf'
                        ).find(
                            'p', class_='auther'
                        ).a
                        thread_author_name = thread_author_obj.get_text()
                        thread_author_id = utils.parse_author_id(thread_author_obj['href'])

                        # TODO: parse the rank of user
                        thread_author = User(
                            user_id=thread_author_id, 
                            name=thread_author_name, 
                            rank=None
                        )

                        # TODO: ask should we count the comment of the author of thread?
                        # comment = Comment(
                        #     author=thread_author, 
                        #     receiver=thread_author, 
                        #     content=''
                        # )
                        # novel_network.add_comment(comment)

                    comment_objs = main_body.findAll(
                        'li', class_='comment-wrap cf'
                    )
                    if not comment_objs:
                        break

                    for comment_obj in comment_objs:
                        comment_author_obj = comment_obj.find(
                            'div', class_='post'
                        ).find(
                            'p', class_='auther'
                        ).a
                        comment_author_name = comment_author_obj.get_text()
                        comment_author_id = utils.parse_author_id(comment_author_obj['href'])
                        comment_content = comment_obj.find(
                            'div', class_='post'
                        ).find(
                            'p', class_='post-body'
                        ).get_text().strip()

                        comment_author = User(
                            user_id=comment_author_id,
                            name=comment_author_name,
                            rank=None
                        )

                        # TODO: parse the content of the comment
                        comment = Comment(
                            author=comment_author, 
                            receiver=thread_author, 
                            content=comment_content
                        )

                        novel_network.add_comment(comment)

                        # print('New Comment:\n%s' % comment)

                print('Has read %d comments of novel %s' % (len(novel_network.comments), novel_id))

            print('Has read %d threads of novel %s' % (thread_num, novel_id))

        # print(novel_network.weights)