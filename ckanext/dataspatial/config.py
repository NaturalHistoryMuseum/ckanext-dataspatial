#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

config = {
    u'query_extent': u'postgis',
    u'postgis.field': u'_geom',
    u'postgis.mercator_field': u'_the_geom_webmercator',
    u'solr.index_field': u'_geom',
    u'solr.latitude_field': u'latitude',
    u'solr.longitude_field': u'longitude'
    }
