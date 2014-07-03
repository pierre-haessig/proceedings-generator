#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Generator for the html files of the proceedings

* html website
* program book (flat doc for printing)
* chairman documents (for session evaluation, for printing)
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
print('Lang set to {}'.format(config['c']['lang']))
print(locale.setlocale(locale.LC_ALL, (config['c']['lang'], 'UTF-8')))


config_vars = config['c']
data = config['data']


# Where to write statictics:
stats_fname = 'SGE_stats.txt'
if stats_fname:
    print('Writing statitics to "{}"'.format(stats_fname))
    stats_file = io.open(stats_fname, 'w', encoding='utf-8') 
else:
    import sys
    print('Writing statitics to stdout')
    stats_file = sys.stdout


### Read and process the list of articles
articles = list(read_articles(join(data['path'], data['article_table'])) )
header, articles = articles[0], articles[1:]

# sort articles list by first author
articles.sort(key= lambda item: item['authors'])
config_vars['articles'] = articles

print('{:d} articles read from table "{}"'.format(
       len(articles), data['article_table']), file=stats_file)

def create_skeleton(render_path):
    '''create the skeleton of directories for the `render_path`
    '''
    subdirs = ['articles', 'images', 'topics', 'sessions']
    if not os.path.isdir(render_path):
        os.mkdir(render_path)
        print('create "{}" directory'.format(render_path))
    
    for sd in subdirs:
        sd = join(render_path, sd)
        if not os.path.isdir(sd):
            os.mkdir(sd)
            print('create "{}" directory'.format(sd))
# end create_skeleton
create_skeleton(data['render_path'])

# Copy pdfs
for art in articles:
    art['pdf'] = manage_pdf(art, data, force_copy=False)

### build topic -> [articles] mapping:
topics = {}

for art in articles:
    top = art['topic']
    if top not in topics:
        topics[top] = []
    # Append article to its topic:
    topics[top].append(art)

print('\nTopics stats', file=stats_file)
print('------------', file=stats_file)
for top in sorted(topics):
    n_art = len(topics[top])
    n_poster = len([art for art in topics[top] if art['media'] == 'poster'])
    n_oral = len([art for art in topics[top] if art['media'] == 'oral'])
    print(' - "{}": {:d} articles'.format(top, n_art), end='\n   ', file=stats_file)
    print('({:d} orals, {:d} posters)'.format(n_oral, n_poster), file=stats_file)

# build topic codes:
topics_code = {top: '{:03d}'.format(idx)
               for idx, top in enumerate(sorted(topics))}

config_vars['topics'] = topics

### build session -> [articles] mapping:
sessions = {}

for art in articles:
    s_id = art['id_session']
    if s_id not in sessions:
        sessions[s_id] = []
    # Append article to its session:
    sessions[s_id].append(art)

# Sort articles in each session using (order, authors)
for s_id in sessions:
    sort_key = lambda art: (art['order'], art['authors'])
    sessions[s_id].sort(key=sort_key)

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

# Build the sessions groups (synchronous sessions)
sessions_groups = {}
for s_id in sessions_details:
    s_date = sessions_details[s_id]['date']
    s_begin = sessions_details[s_id]['begin']
    s_end = sessions_details[s_id]['end']

    if s_date not in sessions_groups:
        sessions_groups[s_date] = {}
    if (s_begin, s_end) not in sessions_groups[s_date]:
        sessions_groups[s_date][s_begin, s_end] = {}

    sessions_groups[s_date][s_begin, s_end][s_id] = sessions_details[s_id]

# Create parallel_next and parallel_prev links
for day, day_group in sessions_groups.iteritems():
    for (begin, end), s_group in day_group.iteritems():
        sorted_ids = sorted(s_group)
        for i, s_id in enumerate(sorted_ids):
            id_next = sorted_ids[(i+1) % len(sorted_ids)]
            id_prev = sorted_ids[(i-1) % len(sorted_ids)]
            ss = s_group[s_id]
            if len(s_group) > 1:
                ss['parallel_next'] = id_next
                ss['parallel_prev'] = id_prev
            else:
                ss['parallel_next'] = None
                ss['parallel_prev'] = None

print('\nSessions stats', file=stats_file)
print('--------------', file=stats_file)
for s_id in sorted(sessions):
    n_art = len(sessions[s_id])
    ss_name = sessions_details[s_id]['name']
    print(' - {:10s} "{}"'.format(s_id, ss_name), file=stats_file, end=': ')
    print('{:d} articles'.format(n_art), file=stats_file)

config_vars['sessions'] = sessions
config_vars['sessions_groups'] = sessions_groups


### build author -> [articles] mapping:
authors = {}

for art in articles:
    art_authors = [name for name, affil in art['authors_split']]
    for auth in art_authors:
        if auth not in authors:
            authors[auth] = []
        # Append article to its author:
        authors[auth].append(art)

# author index:
letter = ''
author_index = {}
for auth in sorted(authors.keys()):
    if auth[0] != letter:
        letter = auth[0]
        author_index[letter] = auth


print('\nAuthors stats:', file=stats_file)
print('{:d} authors found'.format(len(authors)), file=stats_file)

#TODO: nb of authors per article

config_vars['authors']      = authors
config_vars['author_index'] = author_index


### build labs -> [articles] mapping:
labs = {}

for art in articles:
    for lab in art['labs_split']:
        if lab not in labs:
            labs[lab] = []
        # Append article to its lab:
        if art not in labs[lab]:
            labs[lab].append(art)

print('\nLabs stats', file=stats_file)
print('----------', file=stats_file)
print('{:d} labs found'.format(len(labs)), file=stats_file)

for lab in sorted(labs):
    n_art = len(labs[lab])
    plural = 's' if n_art > 1 else ''
    lab = lab.replace(' (France)', '')
    print(' - "{}": {:d} article{}'.format(lab, n_art, plural), file=stats_file)

# Extra stats:
print('\nNumber of labs per article:', file=stats_file)
labs_per_art = {}

for art in articles:
    nb_lab = len(art['labs_split'])
    if nb_lab not in labs_per_art:
        labs_per_art[nb_lab] = 0
    labs_per_art[nb_lab] += 1

for nb_lab in sorted(labs_per_art):
    nb_art = labs_per_art[nb_lab]
    print('{:d} labs: {:3d} articles ({:5.1%})'.format(
           nb_lab, nb_art, nb_art/len(articles)),
          file=stats_file)

config_vars['labs']  = labs

print()

def manage_sponsors(data):
    '''read sponsors data
    
    and copy logo files to `render_path`/images
    '''
    fname_sponsors = join(data['path'], 'sponsors', 'sponsors.csv')

    if os.path.exists(fname_sponsors):
        sponsors  = read_sponsors(fname_sponsors)
        print('{:d} sponsors found'.format(len(sponsors)))
    else:
        sponsors = []
        print('No sponsors')

    print('Copying logo files', end=': ')
    # Copy logo files:
    for spons in sponsors:
        print(spons['logo'], end=', ')
        logo_src = join(data['path'], 'sponsors', spons['logo'])
        logo_dest = join(data['render_path'], 'images', spons['logo'])
        shutil.copyfile(logo_src, logo_dest)
    print()
    
    return sponsors
# end manage_sponsors

config_vars['sponsors'] = manage_sponsors(data)

def copy_static_files(data):
    '''Copy static files to the `render_path`'''
    # list static files:
    from glob import glob
    fname_static_files = glob(join(data['path'], 'static', '*'))
    # copy:
    import subprocess
    subprocess.check_call(['cp', '-r'] + fname_static_files + \
                          [data['render_path']+'/'])
    print('static file copy: {:d} files/directories'.format(
          len(fname_static_files)))
# end copy()
copy_static_files(data)

### Write web pages:

# Create a template "Environment":
templ_path = os.path.dirname(__file__)
loader =  FileSystemLoader(templ_path)
env = Environment(loader=loader, undefined=jinja2.StrictUndefined)
env.globals['topics_code'] = topics_code
env.globals['sessions_details'] = sessions_details
# filters:
# convert list of integers to list of strings
env.filters['int_list_fmt'] = lambda ls:['{:d}'.format(a) for a in ls]

# 1) Index page:
template = env.get_template('index.html')

with io.open(join(data['render_path'], 'index.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 2) List of articles:
template = env.get_template('article_list.html')

with io.open(join(data['render_path'], 'article_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 3) Detailed article pages:
template = env.get_template('article_detail.html')

for art in articles:
    fname = 'article_{:s}.html'.format(art['docid'])
    with io.open(join(data['render_path'], 'articles', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, article=art, root_path='..'))

# 4) Detailed topic pages:
template = env.get_template('topic_detail.html')

for top in topics:
    fname = 'topic_{}.html'.format(topics_code[top])
    with io.open(join(data['render_path'], 'topics', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, topic=top,
                                  articles=topics[top], root_path='..'))

# 5) List of authors:
template = env.get_template('author_list.html')

with io.open(join(data['render_path'], 'author_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 5b) List of labs:
template = env.get_template('lab_list.html')

with io.open(join(data['render_path'], 'lab_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 6a) List of sessions
template = env.get_template('session_list.html')

with io.open(join(data['render_path'], 'session_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))
    
# 6b) Complete program of the sessions (for printed booklet)
template = env.get_template('program_book.html')

with io.open(join(data['render_path'], 'program_book.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 6c) Detailed session pages
template = env.get_template('session_detail.html')

for s_id in sessions:
    fname = 'session_{:s}.html'.format(s_id)
    with io.open(join(data['render_path'], 'sessions', fname),
                 'w', encoding='utf-8') as out:
        out.write(template.render(config_vars, session=sessions_details[s_id], root_path='..'))

# 7) Chairman documents (for session and paper evaluations)
template = env.get_template('chair_eval_session.html')

with io.open(join(data['chair_pkg_path'], 'chairman_package.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# 7b) Chairman documents, split by session
template = env.get_template('chair_eval_index.html')

with io.open(join(data['chair_pkg_path'], 'index.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='.'))

# Close stats
if stats_fname:
    stats_file.close()
