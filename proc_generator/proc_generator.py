#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Generator for the html files of the proceedings
"""

from __future__ import division, print_function, unicode_literals

import os.path
from os.path import join
import io
import jinja2
from jinja2 import Environment, FileSystemLoader

from config import c as config_vars
from data_reader import read_articles

render_path = '../SGE2014_proceedings'
data_path = '../SGE2014_data'

### Read and process the list of articles
articles = list(read_articles(join(data_path,
                              'fichier_retravail_4juin2014.csv')) )
header, articles = articles[0], articles[1:]

# sort articles list by first author
articles.sort(key= lambda item: item['authors'])
config_vars['articles'] = articles

print('{:d} articles read from table ""'.format(len(articles)))


# build topic -> [articles] mapping:
topics = {}

for art in articles:
    top = art['topics']
    if top not in topics:
        topics[top] = []
    # Append article to its topic:
    topics[top].append(art)

print('topics stats:')
for top in topics:
    print(' * "{}": {:d} article(s)'.format(top, len(topics[top])))

# build topic codes:
topics_code = {top: '{:03d}'.format(idx)
               for idx, top in enumerate(sorted(topics))}

config_vars['topics'] = topics
config_vars['topics_code'] = topics_code


# build author -> [articles] mapping:
authors = {}

config_vars['authors'] = {}


### Write web pages:

# Create a template "Environment":
templ_path = os.path.dirname(__file__)
loader =  FileSystemLoader(templ_path)
env = Environment(loader=loader, undefined=jinja2.StrictUndefined)

# 1) Index page:
template = env.get_template('index.html')

with io.open(join(render_path, 'index.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 2) List of articles:
template = env.get_template('article_list.html')

with io.open(join(render_path,'article_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 3) Detailed article pages:
template = env.get_template('article_detail.html')

for art in articles:
    fname = 'article_{:s}.html'.format(art['docid'])
    #print(fname)
    with io.open(join(render_path, 'articles', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, article=art, root_path='..'))

# 4) Detailed topic pages:
template = env.get_template('topic_detail.html')

for top in topics:
    fname = 'topic_{}.html'.format(topics_code[top])
    print(fname)
    with io.open(join(render_path, 'topics', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, topic=top,
                                  articles=topics[top], root_path='..'))



