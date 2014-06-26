#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Create word clouds from articles' abstract
* for each session

using a WordCram (Processing library) script
"""

from __future__ import division, print_function, unicode_literals

from os.path import join
import shutil
import io
import subprocess

try:
    import data_reader
except ImportError:
    import sys
    sys.path.append('../proc_generator')

from data_reader import (
    read_articles, read_sessions)


# Path to the word cram application (standalone exported sketch)
word_cram = '/home/pierre/Programmation/processing_sketch/word_cram_txt/application.linux64/word_cram_txt'

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

### build session -> [articles] mapping:
sessions = {}

for art in articles:
    s_id = art['id_session']
    if s_id not in sessions:
        sessions[s_id] = []
    # Append article to its session:
    sessions[s_id].append(art)

print('articles are grouped in {:d} sessions'.format(len(sessions)))

# Add a special "all_papers" session
sessions['all_papers'] = articles
# Titles only
sessions['all_titles'] = [{'title': art['title'],
                           'abstract': ''}
                          for art in articles]

# Select only some:
#sessions = {key: sessions[key] for key in ['all_titles']}

# Blacklist
black_list = ['K1']
# TODO

### Write session texts:

for s_id in sessions:
    fname_txt = 'words_{}.txt'.format(s_id)
    with io.open(fname_txt, 'w', encoding='utf-8') as out:
        for art in sessions[s_id]:
            out.write(art['title'])
            out.write('\n')
            out.write(art['abstract'])
            out.write('\n')
    print('{:2d} abstracts written to "{}"'.format(len(sessions[s_id]), fname_txt))
    
#    # Run WordCram script:
#    print('Word cloud generation...', end='')
#    subprocess.call([word_cram, fname_txt])
#    print('DONE')
    
    # Inkscape SVG-> PNG conversion
    print('Inkscape conversion...', end='')
    subprocess.call(['inkscape', '--export-area-drawing',
                     '--export-png='+fname_txt.replace('.txt', '.png'),
                     fname_txt.replace('.txt', '.svg')
                    ])
    print('DONE')


