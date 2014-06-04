#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Read CSV table of all contributions to the conference
"""

from __future__ import division, print_function

import io
import csv


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

# Header;
['DOCID',
'TYPE',
'CREATEUSERID',
'MAIL',
'DATE',
'STATUT',
'TYPDOC',
'TOPIC',
'ABSTRACT',
'TITLE',
'MOTCLE',
'SPEAKERS',
'AUTHORS',
'LABOS',
'FILE',
'FILE_SRC']


def article_iterator(fname):
    with io.open(fname, encoding='utf-8') as f:
        c = csv.reader(utf_8_encoder(f), delimiter=';')
        
        # 1) Read the headers
        header = c.next()
        header = [head.lower() for head in header]
        
        for line in c:
            item = {head: line[idx].decode('utf-8') for idx, head in enumerate(header)}
            if item['type'] != u'FULLTEXT' or \
               item['statut'] != u'Accepté':
                # filters out the ABSTRACT contributions
                # or not yet accepted papers
                continue

            yield item


if __name__ == '__main__':
    # Example:
    articles = article_iterator('../SGE2014_data/fichier_brut_4juin2014.csv')
    articles = list(articles)
    
    print(articles[0])
    print('nb articles: {:d}'.format(len(articles)))
