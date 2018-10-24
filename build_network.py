
# coding: utf-8

# In[1]:


novel_id = '8161510403317103'
comment_file = 'data/CommentInfo-%s.csv' % novel_id
cleaned_comment_file = 'data/CleanedCommentInfo-%s.csv' % novel_id
post_file = 'data/PostInfo-%s.csv' % novel_id
node_file = 'data/Node-%s.csv' % novel_id
edge_file = 'data/Edge-%s.csv' % novel_id


# In[2]:


from collections import namedtuple
NodeInfo = namedtuple('NodeInfo', ['label', 'attribute'])
EdgeInfo = namedtuple('EdgeInfo', ['type', 'appearance', 'textLength'])
EdgeInfo.__new__.__defaults__ = ('Directed', 0, 0)
RealNode = namedtuple('RealNode', ['id', 'nodeInfo'])
RealEdge = namedtuple('RealEdge', ['source', 'target', 'edgeInfo'])


# In[3]:


from collections import defaultdict


# In[4]:


post2author = dict()
with open(post_file, 'r') as f:
    for line in f:
        author_name, author_id, post_id = line.strip().split(', ')
        post2author[post_id] = author_id


# In[5]:


has_processed_post = set()
nodes = dict()
edges = defaultdict(EdgeInfo)
with open(comment_file, 'r') as f, open(cleaned_comment_file, 'w+') as g:
    for line in f:
        try:
            author_name, author_id, post_id, *context = (line.strip()+' ').split(', ')
            context = ','.join(context)
            author_name = author_name or '_'
            print('\t'.join([author_name, author_id, post_id, context]), file=g)
        except ValueError:
            pass
        
        if author_id not in nodes:
            *attribute, label = author_name.split()
            if not attribute:
                attribute = None
            else:
                attribute = attribute[0]
            nodes[author_id] = NodeInfo(label=label, attribute=attribute)
        
        if post_id not in has_processed_post:
            assert post2author[post_id] == author_id
            has_processed_post.add(post_id)
        else:
            source = author_id
            target = post2author[post_id]
            oldEdgeInfo = edges[(source, target)]
            newEdgeInfo = EdgeInfo(
                appearance=oldEdgeInfo.appearance+1, 
                textLength=oldEdgeInfo.textLength+len(context)
            )
            edges[(source, target)] = newEdgeInfo


# In[6]:


realEdges = []
for keypair, edge in edges.items():
    realEdges.append(RealEdge(source=keypair[0], target=keypair[1], edgeInfo=edge))


# In[7]:


# sorted(realEdges, key=lambda x:x.edgeInfo.appearance, reverse=True)[:10]


# In[8]:


with open(node_file, 'w+') as f:
    print('Id, Label, Attribute', file=f)
    for node_id, node in nodes.items():
        print(node_id, node.label, node.attribute, sep=', ', file=f)


# In[9]:


with open(edge_file, 'w+') as f:
    print('Source, Target, Type, Appearance, TextLength', file=f)
    for e in realEdges:
        print(e.source, e.target, e.edgeInfo.type, e.edgeInfo.appearance, e.edgeInfo.textLength, sep=', ', file=f)

