# -*- coding: utf-8 -*-
"""Configuration of the proceedings generator

* where to find data
* parameters of the event (name, date, ...)
"""

from __future__ import unicode_literals

### Main configuration parameters

data = {}
# Input data:
data['path'] = '../SGE2014_data'
data['article_table'] = 'bilan_papiers_programme.csv'
data['session_table'] = 'sessions.csv'
# Output path:
data['render_path'] = '../SGE2014_proceedings'
data['chair_pkg_path'] = '../chairman package'


### Event parameters dict
c={}

# language, for <html lang="xx"> attribute:
c['lang'] = 'fr'

# Event (conference) parameters:
c['event_name'] = 'SGE 2014'
c['event_date'] = '8—10 juillet 2014'
c['event_location']= 'Cachan (France)'
c['event_website'] = 'http://sge2014.sciencesconf.org/'
c['event_logo'] = 'logo_sge.png'

c['website_credits'] = 'Pierre Haessig, laboratoire SATIE'
