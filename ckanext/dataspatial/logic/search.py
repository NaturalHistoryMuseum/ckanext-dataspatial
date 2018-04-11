#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

from ckanext.dataspatial.config import config
from ckanext.dataspatial.lib.postgis import query_extent as postgis_query_extent
from ckanext.dataspatial.lib.solr import query_extent as solr_query_extent


def datastore_query_extent(context, data_dict):
    '''Return the geospatial extent of a given datastore queries.
    
    The arguments as per `datastore_search`, and the return value defines:
    {
        'total_count': Total number of rows matching the query,
        'geom_count': Number of rows matching the query that have geospatial
                      information
        'bounds': ((lat min, long min), (lat max, long max)) for the
                  queries rows
    }

    :param context: Current context
    @data_dict: Request arguments, as per datastore_search
    :param data_dict: 

    '''
    # if config['query_extent'] == 'solr':
    #     return solr_query_extent(data_dict)
    # else:
    return postgis_query_extent(data_dict)
