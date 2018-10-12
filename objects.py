from collections import namedtuple
import utils

EdgeWeights = namedtuple('EdgeWeights', ['count', 'len_sum'])

class User(object):
    """
    The object of an user.

    Args:
        user_id : str
            Every user has their own unique id, shown in their own user info URL.
            For example, if the info URL of an user is https://my.qidian.com/user/214164933,
            the user_id is '214164933'.

        name : str
            The name of the user.
        
        rank : str / None
            The rank of the user.
            The rank may be one of the ['舵主', '堂主', '护法', '长老', '掌门', '宗师', '盟主', '本书作者'].
            Else, the rank is None.
    """
    def __init__(self, user_id, name, rank):
        self.user_id = user_id
        self.name = name
        self.rank = rank

    def __hash__(self):
        return hash(self.user_id)
    
    def __eq__(self, that):
        if not isinstance(that, User):
            return False
        return self.user_id == that.user_id

    def __repr__(self):
        return '<User object id=%s name=%s rank=%s>' % (self.user_id, self.name, self.rank)

class Reply(object):
    """
    The object of a reply to the comment.

    Args:
        author : User Object
            The author of the reply.

        content : str
            The content of the reply.
    """
    def __init__(self, author, content):
        self.author = author
        self.content = content

    def __repr__(self):
        return '<Reply object\n\tauthor=%s\n\treceiver=%s\n\tcontent=%s\n>' % \
               (self.author, self.receiver, self.content)

class Comment(object):
    """
    The object of an comment in the post.

    Args:
        author : User Object
            The author of the comment.

        content : str
            The content of the comment.
    """
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.replies = []

    def __repr__(self):
        return '<Comment object\n\tauthor=%s\n\treceiver=%s\n\tcontent=%s\n>' % \
               (self.author, self.receiver, self.content)
    
    def add_reply(self, reply):
        self.replies.append(reply)

class Post(object):
    """
    The object of an post in the forum of the novel.

    Args:
        author : User Object
            The author of the post.

        content : str
            The content of the post,
            in other words, the top comment in the post.
    """
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.comments = []
    
    def __repr__(self):
        return '<Post object\n\tauthor=%s\n\tcontent=%s\n>' % \
                (self.author, self.content)
    
    def add_comment(self, comment):
        self.comments.append(comment)

class Novel(object):
    """
    The object of the whole forum content of the model.

    Args:
        novel_id : str
            Every novel has its own unique id, shown in the URL of the forum of the novel.
            For example, if the forum URL of a novel is https://forum.qidian.com/index/5776840004868003,
            the user_id is '5776840004868003'.
        
        author : User Object
            The author of the novel.

        posts : list of Post Object
            The posts in the forum.
        
        involved_users : set of User Object
            All the users appeared in the posts / comments / replies in the forum.
        
        weights : dict of (key=(User Object, User Object), value=EdgeWeights(count, len_sum))
            The weights of the whole network of the forum.
            
            The key of the dict is a tuple of two User Objects, 
            the first one is the author, and the second one is the receiver.
            There exists a key of (User1, User2) if:
                (a) User2 has a post, and User1 comments to it.
                (b) User2 has a comment in the post, and User1 replies to it.
            
            The value of the dict is a namedtuple of two int,
            the first one implies the frequency (appearance) of the key,
            the second one implies the total character number of the content in the comments / replies.
        
    """
    def __init__(self, novel_id, author=None):
        self.novel_id = novel_id
        self.author = author
        self.posts = []
        self.involved_users = set()
        self._weights = {}
    
    def add_post(self, post):
        self.posts.append(post)
    
    def _update_edges(self, author, receiver, content):
        self.involved_users.update([author, receiver])
        edge = (author, receiver)
        old_weights = self._weights.get(edge, EdgeWeights(count=0, len_sum=0))
        self._weights[edge] = EdgeWeights(
            count=old_weights.count + 1, 
            len_sum=old_weights.len_sum + len(content)
        )
    
    def calculate(self):
        if self._weights:
            return self._weights
        else:
            for post in self.posts:
                for comment in post.comments:
                    self._update_edges(comment.author, post.author, comment.content)
                    for reply in comment.replies:
                        self._update_edges(reply.author, comment.author, reply.content)
            return self._weights

class FlushNovel(Novel):
    """
    The object of the whole forum content of the model.
    Due to the memory issue, this version of Novel Object will update the output file
    when crawling a new post.
    
    Args:
        novel_id : str
            Every novel has its own unique id, shown in the URL of the forum of the novel.
            For example, if the forum URL of a novel is https://forum.qidian.com/index/5776840004868003,
            the user_id is '5776840004868003'.
            
        author : User Object
            The author of the novel.

        file_prefix : str
            The prefix of the filename of the data.
            If file_prefix is 'abc', 
            then the node file will be 'abc_node.csv'
            and the edge file will be 'abc_edge.csv'

        max_post_num : int
            The max number of stored posts.

        posts : list of Post Object
            The posts in the forum.
            Deprecated in FlushNovel Object.

        involved_users : set of User Object
            All the users appeared in the posts / comments / replies in the forum.
            # NOTICE: involved_users will be reset every time when crawling max_post_num new post(s).
        
        weights : dict of (key=(User Object, User Object), value=EdgeWeights(count, len_sum))
            The weights of the whole network of the forum.
            
            The key of the dict is a tuple of two User Objects, 
            the first one is the author, and the second one is the receiver.
            There exists a key of (User1, User2) if:
                (a) User2 has a post, and User1 comments to it.
                (b) User2 has a comment in the post, and User1 replies to it.
            
            The value of the dict is a namedtuple of two int,
            the first one implies the frequency (appearance) of the key,
            the second one implies the total character number of the content in the comments / replies.
            # NOTICE: weights will be reset every time when crawling max_post_num new post(s).
    """
    def __init__(self, novel_id, author=None, file_prefix=None, max_post_num=30):
        super().__init__(novel_id, author)
        self.file_prefix = file_prefix
        self.max_post_num = max_post_num
        assert isinstance(max_post_num, int) and max_post_num > 0, \
            'The max_post_num argument should be greater than 0'
        self.post_num = 0

    def add_post(self, post, last=True):
        self.post_num += 1
        for comment in post.comments:
            self._update_edges(comment.author, post.author, comment.content)
            for reply in comment.replies:
                self._update_edges(reply.author, comment.author, reply.content)

        if last or self.post_num % self.max_post_num == 0:
            self._update_file()

    def _update_edges(self, author, receiver, content, write=True):

        self.involved_users.update([author, receiver])
        edge = (author, receiver)
        old_weights = self._weights.get(edge, EdgeWeights(count=0, len_sum=0))
        self._weights[edge] = EdgeWeights(
            count=old_weights.count + 1, 
            len_sum=old_weights.len_sum + len(content)
        )

    def _update_file(self):
        utils.write_weights_of_novel(self, file_prefix=self.file_prefix, mode='a')
        utils.write_users_of_novel(self, file_prefix=self.file_prefix, mode='a')

        self.involved_users = set()
        self._weights = {}

    def calculate(self):
        raise NotImplementedError
