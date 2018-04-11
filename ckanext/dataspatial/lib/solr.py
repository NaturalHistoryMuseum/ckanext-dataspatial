#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

import copy

from ckanext.dataspatial.config import config

from ckan.plugins import toolkit


def query_extent(data_dict):
    '''Return the spatial query extent of a datastore search

    :param data_dict: Dictionary defining the search
    :returns: s a dictionary defining:
        {
            total_count: The total number of rows in the query,
            geom_count: The number of rows that have a geom,
            bounds: ((lat min, long min), (lat max, long max)) for the
                  queries rows
        }

    '''
    lat_field = config[u'solr.latitude_field']
    long_field = config[u'solr.longitude_field']
    result = {
        u'total_count': 0,
        u'geom_count': 0,
        u'bounds': None
        }
    data_dict = copy.deepcopy(data_dict)
    data_dict[u'offset'] = 0
    data_dict[u'limit'] = 1
    data_dict[u'fields'] = [u'_id']
    r = toolkit.get_action(u'datastore_search')({}, data_dict)
    if r[u'total'] == 0:
        return result
    result[u'total_count'] = r[u'total']
    # data_dict['solr_stats_fields'] = [lat_field, long_field]
    if u'filters' not in data_dict:
        data_dict[u'filters'] = {}
    # data_dict['filters']['_solr_not_empty'] = [lat_field, long_field]

    r = toolkit.get_action(u'datastore_search')({}, data_dict)
    if r[u'total'] == 0:
        return result
    result[u'geom_count'] = r[u'total']
    bounds = [[0, 0], [0, 0]]
    for field_def in r[u'fields']:
        if field_def[u'id'] == lat_field:
            bounds[0][0] = field_def[u'min']
            bounds[1][0] = field_def[u'max']
        elif field_def[u'id'] == long_field:
            bounds[0][1] = field_def[u'min']
            bounds[1][1] = field_def[u'max']
    result[u'bounds'] = (
        tuple(bounds[0]), tuple(bounds[1])
        )
    return result
