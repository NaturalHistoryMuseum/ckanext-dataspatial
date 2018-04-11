#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = '0.2'

with open(u'ckanext/dataspatial/version.py') as f:
    exec (f.read())

setup(
    name=u'ckanext-dataspatial',
    version=__version__,
    description=u'Ckan extension to provide geospatial awareness of datastore datasets',
    url=u'http://github.com/NaturalHistoryMuseum/ckanext-dataspatial',
    packages=find_packages(exclude=u'tests'),
    entry_points=u'''
        [ckan.plugins]
            dataspatial = ckanext.dataspatial.plugin:DataSpatialPlugin
        [paste.paster_command]
            dataspatial = ckanext.dataspatial.commands.dataspatial:DataSpatialCommand''')
