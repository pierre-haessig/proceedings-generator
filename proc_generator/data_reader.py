#!/usr/bin/python
# -*- coding: utf-8 -*-
# Pierre Haessig — June 2014
""" Read CSV table of all contributions to the conference
"""

from __future__ import division, print_function

import io
import csv
import re
import datetime
import os.path
from os.path import join
import shutil


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def decode_labs(labs):
    '''matches labs strings like
    '1 - Dpt. Energie, SUPELEC-Campus Gif, 2 - Laboratoire L2EP'

    Returns the list of labs' name.
    ['Dpt. Energie, SUPELEC-Campus Gif', 'Laboratoire L2EP']
    '''
    labs = re.findall('(^\d - |, \d - )(.*?)(?=, \d - |$)', labs)
    labs = [lab for (idx, lab) in labs]
    return labs


def read_articles(fname):
    '''read CSV table of the articles contributed to the conference
    
    Returns a generator
    '''
    re_affil = re.compile(r'\((\d+)\)')
    
    with io.open(fname, encoding='utf-8') as f:
        c = csv.reader(utf_8_encoder(f), delimiter=';')
        
        # 1) Read the headers
        header = c.next()
        header = [head.lower() for head in header]
        yield header
        
        for line in c:
            item = {head: line[idx].strip().decode('utf-8')
                    for idx, head in enumerate(header)}
            
            # Manually fill blanks:
            if item['topic'] == '':
                item['topic'] = 'no topic'
            if item['id_session'] == '':
                item['id_session'] = 'SO-XX-X'
            
            # Process the authors field to split names
            authors = item['authors'].split(', ')
            authors_split = []
            
            for auth in authors:
                # Affiliation(s):
                affil = re_affil.findall(auth)
                affil = [int(ai) for ai in affil]
                # Author name:
                name, count = re_affil.subn('', auth)
                assert len(affil) == count
                name = name.strip()
                
                authors_split.append((name, affil))
            # end for each author
            item['authors_split'] = authors_split
            item['authors_no_affil'] = ', '.join(
                [name for (name, affil) in authors_split])
            
            # Process labs name:
            item['labs_split'] = decode_labs(item['labos'])
            
            yield item


def read_sponsors(fname):
    '''read CSV table of the sponsors
    
    Returns a list of dict, with 3 keys: 'name', 'url', 'logo'
    '''
    with io.open(fname, encoding='utf-8') as f:
        c = csv.reader(utf_8_encoder(f))
        
        # 1) Read the headers
        header = c.next()
        assert header == ['name', 'url', 'logo']
        
        sponsors = []
        for line in c:
            if len(line) < len(header): continue
            sponsors.append({
                'name': line[0].decode('utf-8'),
                'url':  line[1].decode('utf-8'),
                'logo': line[2].decode('utf-8'),
                })
        
        return sponsors

def decode_hour(s):
    'decode "11:30" into (11, 30)'
    h,m = s.split(':')
    return int(h), int(m)

def decode_date(s):
    d,m,y = s.split('/')
    return datetime.date(int(y), int(m), int(d))

def split_chairmen(chairmen):
    split = chairmen.split(';')
    split = [name.strip() for name in split]
    return split

def read_sessions(fname):
    '''read CSV table of the sessions description
    
    Returns a dict of session dict
     'session_id' -> {'name': 'session name', 'location': 'some place', 'date': ....}
    '''
    with io.open(fname, encoding='utf-8') as f:
        c = csv.reader(utf_8_encoder(f))
        
        # 1) Read the headers
        header = c.next()
        assert header == ['id', 'type', 'name', 'nb papiers', 'location', 'date', 'begin', 'end', 'chairmen']
        
        sessions = {}
        for line in c:
            if len(line) < len(header): continue
            details = {head: line[idx].decode('utf-8') for idx, head in enumerate(header)}
            s_id = details['id']
            
            day = decode_date(details['date'])
            details['date'] = day
            h,m = decode_hour(details['begin'])
            details['begin'] = datetime.datetime(
                day.year, day.month, day.day, h, m)
            h,m = decode_hour(details['end'])
            details['end'] = datetime.datetime(
                day.year, day.month, day.day, h, m)
            
            details['chairmen_split'] = split_chairmen(details['chairmen'])
            
            sessions[s_id] = details

        return sessions

def manage_pdf(art, data_config, force_copy=False):
    '''find article's pdf file and copy it to the render_path
    
    Returns
    -------
    path to the copied pdf file (if found), relative to render_path
        None if pdf source is not found.
    '''
    source_path = data_config['path']
    render_path = data_config['render_path']
    
    pdf_source = join(source_path, 'articles', art['docid']+'.pdf')
    pdf_dest = join('articles', 'article_'+art['docid']+'.pdf')
    if not os.path.exists(pdf_source):
        print('article {} has no PDF!'.format(art['docid']))
        return None
    else:
        if not os.path.exists(join(render_path, pdf_dest)) or force_copy:
            shutil.copyfile(pdf_source, join(render_path, pdf_dest))
        return pdf_dest

if __name__ == '__main__':
    # Example:
    articles = read_articles('../SGE2014_data/bilan_papiers_programme.csv')
    articles = list(articles)
    
    header, articles = articles[0], articles[1:]
    
    print('Header:')
    print(', '.join(header))
    
    print('One article:')
    print(articles[0]['title'])
    print('nb articles: {:d}'.format(len(articles)))
