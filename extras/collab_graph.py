#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Analyze collaboration between labs using conference data:
each jointly written article creates a link.
"""

from __future__ import division, print_function, unicode_literals

from os.path import join
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

try:
    import data_reader
except ImportError:
    import sys
    sys.path.append('../proc_generator')

from data_reader import (
    read_articles, read_sessions)

### Read configuration
config = {}
execfile('../proc_generator/config.py', {}, config)

config_vars = config['c']
data = config['data']

### Read and process the list of articles
articles = list(read_articles(join(data['path'], data['article_table'])) )
header, articles = articles[0], articles[1:]

# sort articles list by first author
articles.sort(key= lambda item: item['authors'])

print('{:d} articles read from table "{}"'.format(len(articles),
                                                data['article_table']))

# Some stats:
labs_per_art = {}

for art in articles:
    nb_lab = len(art['labs_split'])
    if nb_lab not in labs_per_art:
        labs_per_art[nb_lab] = 0
    labs_per_art[nb_lab] += 1

print('Stats: number of labs per article:')
for nb_lab in sorted(labs_per_art):
    nb_art = labs_per_art[nb_lab]
    print('{:d} labs: {:3d} articles ({:5.1%})'.format(
          nb_lab, nb_art, nb_art/len(articles)) )

### Build the collaboration graph:

# data dict:
collab = {}
article_cnt = {}

def name_fix(lab):
    lab = lab.replace(' (France)', '')
    return lab
    
def name_format(lab):
    split = lab.split(' ')
    # Put some '\n'
    stack = [split[0]]
    for s in split[1:]:
        if len(stack[-1] + s) < 15:
            stack[-1] = stack[-1] + ' ' + s
        else:
            stack.append(s)
    
    lab = '\n'.join(stack)
    return lab

# browse articles:
for art in articles:
    labs = [name_fix(lab) for lab in art['labs_split']]
    labs = set(labs)
    # browse all pairs:
    for l1, l2 in combinations(labs, 2):
        # 1) mark l1 -> l2
        if not l1 in collab:
            collab[l1] = {}
        if not l2 in collab[l1]:
            collab[l1][l2] = 0
        collab[l1][l2] += 1
#        # 2) mark l2 -> l1
#        if not l2 in collab:
#            collab[l2] = {}
#        if not l1 in collab[l2]:
#            collab[l2][l1] = 0
#        collab[l2][l1] += 1
    # Count articles:
    for lab in labs:
        if lab not in article_cnt:
            article_cnt[lab] = 0
        article_cnt[lab] += 1


### Convert to networkx graph:

def edge_gen(collab, thres=1):
    for l1 in collab:
        for l2 in collab[l1]:
            cnt = collab[l1][l2]
            if cnt >= thres:
                yield (l1, l2, {'weight': 1./cnt})

G = nx.Graph()

G.add_edges_from(edge_gen(collab, 1))

pos = nx.spring_layout(G, weight='weight')
# Graphviz layout:
#pos = nx.graphviz_layout(G, 'neato', args='-Goverlap=false')

### Draw:
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111)

# nodes
node_size = [50*article_cnt[lab] for lab in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=node_size,
                       node_color='#99caff', linewidths=0.1)

fonts = dict(font_size=5,font_family='sans-serif')
nx.draw_networkx_labels(G, pos, labels = {lab: name_format(lab) for lab in G.nodes()}, **fonts)


edge_width = [3*e[2]['weight'] for e in G.edges(data=True)]
nx.draw_networkx_edges(G, pos, width=edge_width,
                       edge_color='#FFAA00', alpha=0.5)

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.xlim(-0.06, 1.06)
plt.ylim(-0.06, 1.06)
plt.axis('off')
plt.show()
fig.savefig('collab_spring2.png', dpi=200, bbox_inches='tight')
