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
from read_article_csv import read_articles

render_path = '../SGE2014_proceedings'
data_path = '../SGE2014_data'

templ_path = os.path.dirname(__file__)
loader =  FileSystemLoader(templ_path)
env = Environment(loader=loader, undefined=jinja2.StrictUndefined)

# Home:
template = env.get_template('home.html')


with io.open(join(render_path,'home.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='./'))

# List of articles:
template = env.get_template('article_list.html')

articles = list(read_articles(join(data_path,
                              'fichier_retravail_4juin2014.csv')) )
header, articles = articles[0], articles[1:]

articles.sort(key= lambda item: item['authors'])


config_vars['articles'] = articles

with io.open(join(render_path,'article_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars, root_path='./'))

