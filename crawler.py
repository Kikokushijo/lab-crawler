import re

import utils
from objects import User, Comment, Post, Novel

# settings
novel_ids = ['11495791504803003']

def get_post_objs_of_novel(novel_id):
    post_prefix = '//forum.qidian.com/post/%s' % novel_id
    post_page_num = 0
    post_objs = []
    
    while True:
        post_page_num += 1
        post_entry = utils.get_post_entry(
            novel_id=novel_id, 
            page_num=post_page_num
        )
        _post_objs = post_entry.findAll(
            'div', class_='post', 
        )

        _post_objs = [
            post_obj.find(
                'a', {
                 'target': '_blank',
                 'href': re.compile("^%s" % post_prefix)
                }
            ) for post_obj in _post_objs
        ]

        # if there is no posts in new page
        if not _post_objs:
            break
        else:
            post_objs.extend(_post_objs)
    
    return post_objs

def get_network_of_post(post_obj):
    comment_page_num = 0
    comment_objs = []
    post = None
    
    while True:
        comment_page_num += 1
        _comment_objs = utils.get_comment_entry(
            post_id=post_obj.attrs['href'], 
            page_num=comment_page_num
        )
        _comment_objs = _comment_objs.find(
            'div', class_='main-body fl'
        )

        # there is the author of the post
        if comment_page_num == 1:

            post_author_obj = _comment_objs.find(
                'div', class_='post-wrap cf'
            ).find(
                'p', class_='auther'
            ).a
            
            post_author_id = utils.parse_author_id(post_author_obj['href'])
            post_author_name, post_author_rank = \
                utils.parse_author_name(post_author_obj.get_text())
            
            post_author = User(
                user_id=post_author_id, 
                name=post_author_name, 
                rank=post_author_rank
            )
            
            # TODO: parse the content of the post
            post = Post(author=post_author, content=None)

            # TODO: ask should we count the comment of the author of post?
            # comment = Comment(
            #     author=post_author, 
            #     receiver=post_author, 
            #     content=''
            # )
            # post.add_comment(comment)
        
        _comment_objs = _comment_objs.findAll(
            'li', class_='comment-wrap cf'
        )
        
        if not _comment_objs:
            break
    
        comment_objs.extend(list(_comment_objs))

    for comment_obj in comment_objs:
        
        comment_author_obj = comment_obj.find(
            'div', class_='post'
        ).find(
            'p', class_='auther'
        ).a
        
        comment_author_id = utils.parse_author_id(comment_author_obj['href'])
        comment_author_name, comment_author_rank = \
            utils.parse_author_name(comment_author_obj.get_text())
        comment_content = comment_obj.find(
            'div', class_='post'
        ).find(
            'p', class_='post-body'
        ).get_text().strip()

        comment_author = User(
            user_id=comment_author_id,
            name=comment_author_name,
            rank=comment_author_rank
        )

        comment = Comment(
            author=comment_author, 
            content=comment_content
        )

        post.add_comment(comment)
            
    # TODO: parse the dynamic reply of the comment
    
    return post


if __name__ == '__main__':

    for novel_id in novel_ids:
        print('Now crawling the novel_id %s...' % novel_id)
        novel = Novel(novel_id=novel_id)
        post_objs = get_post_objs_of_novel(novel_id)
        for post_obj in post_objs:
            post = get_network_of_post(post_obj)
            novel.add_post(post)

        # print('Now calculating the weights...')
        # weights = novel.calculate()

        print('Now writing the weights to file...')
        utils.write_weights_of_novel(novel)
        
        print('Now writing the users to file...')
        utils.write_users_of_novel(novel)

        print('Finish the processing of novel_id %s...' % novel_id)

