from collections import namedtuple

EdgeWeights = namedtuple('EdgeWeights', ['count', 'len_sum'])

class User(object):
    def __init__(self, user_id, name, rank):
        self.user_id = user_id
        self.name = name
        self.rank = rank

    def __hash__(self):
        return hash(self.user_id)

    def __repr__(self):
        return '<User id=%s name=%s rank=%s>' % (self.user_id, self.name, self.rank)

class Comment(object):
    def __init__(self, author, receiver, content, time=None):
        self.author = author
        self.receiver = receiver
        self.content = content
        self.time = time

    def __repr__(self):
        return '<Comment \n\tauthor=%s \n\treceiver=%s \n\tcontent=%s\n>' % (self.author, self.receiver, self.content)

class NovelComments(object):
    def __init__(self, novel_id, author=None):
        self.novel_id = novel_id
        self.author = author
        self.comments = []
        self.involved_users = set()
        self.weights = {}

    def add_comment(self, comment):
        self.comments.append(comment)
        self.involved_users.update([comment.author, comment.receiver])
        
        edge = (comment.author, comment.receiver)
        if edge in self.weights:
            old_weights = self.weights[edge]
        else:
            old_weights = EdgeWeights(count=0, len_sum=0)
        
        self.weights[edge] = EdgeWeights(
            count=old_weights.count + 1, 
            len_sum=old_weights.len_sum + len(comment.content)
        )