#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Generator for the html files of the proceedings
"""

from __future__ import division, print_function, unicode_literals

import os.path
from os.path import join
import shutil
import io
import jinja2
from jinja2 import Environment, FileSystemLoader

from data_reader import read_articles, read_sponsors

### Read configuration
config = {}
execfile('config.py', {}, config)

config_vars = config['c']
data = config['data']


### Read and process the list of articles
articles = list(read_articles(join(data['path'], data['article_table'])) )
header, articles = articles[0], articles[1:]

# sort articles list by first author
articles.sort(key= lambda item: item['authors'])
config_vars['articles'] = articles

print('{:d} articles read from table "{}"'.format(len(articles),
                                                data['article_table']))


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


# build author -> [articles] mapping:
authors = {}

config_vars['authors'] = {}

# Read the sponsors:
fname_sponsors = join(data['path'], data['sponsor_table'])

if os.path.exists(fname_sponsors):
    sponsors  = read_sponsors(fname_sponsors)
    print('{:d} sponsors found'.format(len(sponsors)))
else:
    sponsors = []
    print('No sponsors')

config_vars['sponsors'] = sponsors

print('Copying logo files', end=': ')
# Copy logo files:
for spons in sponsors:
    print(spons['logo'], end=', ')
    logo_src = join(data['path'], spons['logo'])
    logo_dest = join(data['render_path'], 'images', spons['logo'])
    shutil.copyfile(logo_src, logo_dest)
print()

### Write web pages:

# Create a template "Environment":
templ_path = os.path.dirname(__file__)
loader =  FileSystemLoader(templ_path)
env = Environment(loader=loader, undefined=jinja2.StrictUndefined)
env.globals['topics_code'] = topics_code

# 1) Index page:
template = env.get_template('index.html')

with io.open(join(data['render_path'], 'index.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 2) List of articles:
template = env.get_template('article_list.html')

with io.open(join(data['render_path'],'article_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 3) Detailed article pages:
template = env.get_template('article_detail.html')

for art in articles:
    fname = 'article_{:s}.html'.format(art['docid'])
    #print(fname)
    with io.open(join(data['render_path'], 'articles', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, article=art, root_path='..'))

# 4) Detailed topic pages:
template = env.get_template('topic_detail.html')

for top in topics:
    fname = 'topic_{}.html'.format(topics_code[top])
    print(fname)
    with io.open(join(data['render_path'], 'topics', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, topic=top,
                                  articles=topics[top], root_path='..'))



