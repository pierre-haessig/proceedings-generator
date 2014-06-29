#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Generator for the printed "Chairman packages"

* evaluation of the sessions
* evaluation of each presentation of the sessions
"""

from __future__ import division, print_function, unicode_literals

import os.path
from os.path import join
import shutil
import io
import locale
import jinja2
from jinja2 import Environment, FileSystemLoader

import data_reader
reload(data_reader)

from data_reader import (
    read_articles, read_sponsors, read_sessions,
    manage_pdf)

### Read configuration
config = {}
execfile('config.py', {}, config)

# locale (for time formatting)
assert locale.getdefaultlocale()[0][0:2] == config['c']['lang']

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

### build session -> [articles] mapping:
sessions = {}

for art in articles:
    s_id = art['id_session']
    if s_id not in sessions:
        sessions[s_id] = []
    # Append article to its session:
    sessions[s_id].append(art)

# Read session description
fname_sessions = join(data['path'], data['session_table'])

sessions_details = read_sessions(fname_sessions)

# Check that each session used in article table has a description:
for s_id in sessions:
    assert s_id in sessions_details

# put empty list of articles for unused sessions
for s_id in sessions_details:
    if s_id not in sessions:
        sessions[s_id] = []

config_vars['sessions'] = sessions

### Write web pages:

# Create a template "Environment":
templ_path = os.path.dirname(__file__)
loader =  FileSystemLoader(templ_path)
env = Environment(loader=loader, undefined=jinja2.StrictUndefined)
env.globals['sessions_details'] = sessions_details
# filters:
# convert list of integers to list of strings
env.filters['int_list_fmt'] = lambda ls:['{:d}'.format(a) for a in ls]

# Session evaluation:
template = env.get_template('chair_eval_session.html')

with io.open(join(data['chair_pkg_path'], 'chairman_package.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))
