#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Generator for the html files of the proceedings
"""

from __future__ import division, print_function, unicode_literals

import os.path
import io
import jinja2
from jinja2 import Environment, FileSystemLoader

from config import c as config_vars
import read_article_csv

render_path = '../SGE2014_proceedings'
data_path = '../SGE2014_data'

templ_path = os.path.dirname(__file__)
loader =  FileSystemLoader(templ_path)
env = Environment(loader=loader, undefined=jinja2.StrictUndefined)

# Home:
template = env.get_template('home.html')


with io.open(os.path.join(render_path,'home.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars))

# List of articles
template = env.get_template('article_list.html')

articles = read_article_csv.article_iterator(os.path.join(data_path,'fichier_brut_4juin2014.csv'))

config_vars['articles'] = articles

with io.open(os.path.join(render_path,'article_list.html'),
             'w', encoding='utf-8') as out:
    out.write(template.render(config_vars))

