
# coding: utf-8

# In[1]:


import sys
# novel_id = '8161510403317103'
novel_id = sys.argv[1]
comment_file = 'data/%s/CommentInfo-%s.csv' % (novel_id, novel_id)
post_file = 'data/%s/PostInfo-%s.csv' % (novel_id, novel_id)
node_file = 'data/%s/Filter-Node-%s.csv' % (novel_id, novel_id)
edge_file = 'data/%s/Filter-Edge-%s.csv' % (novel_id, novel_id)


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
        author_name, author_id, post_id = line.strip().split('\t')
        post2author[post_id] = author_id


# In[5]:

def filter_func(source, target, context):
    if source == target:
        return False
    if len(context) <= 5:
        return False
    return True


has_processed_post = set()
nodes = dict()
edges = defaultdict(EdgeInfo)
with open(comment_file, 'r') as f:
    assert f.readline().strip() == 'START'
    for line in f:
        if line.strip() == 'END':
            break
        try:
            author_name, author_id, post_id, *context = (line.strip()).split('\t')
            context = '\t'.join(context)
            author_name = author_name or '--NAN--'
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
            # assert post2author[post_id] == author_id
            has_processed_post.add(post_id)
        else:
            source = author_id
            target = post2author[post_id]

            if not filter_func(source, target, context):
                continue

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

