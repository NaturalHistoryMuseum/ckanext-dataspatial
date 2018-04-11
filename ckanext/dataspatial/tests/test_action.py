#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

from ckanext.dataspatial.config import config
from ckanext.dataspatial.logic.action import (create_geom_columns,
                                              update_geom_columns)
from ckanext.dataspatial.logic.search import datastore_query_extent
from mock import patch
from nose.tools import assert_equals, assert_raises

from ckan.plugins import toolkit


class TestActions(object):
    ''' '''

    def test_create_geom_columns_requires_resource_id(self):
        '''Ensure the create_geom_columns action raises if resource_id is not
             provided.


        '''
        assert_raises(toolkit.ValidationError, create_geom_columns, {}, {})

    @patch(u'ckanext.dataspatial.logic.action.create_postgis_columns')
    @patch(u'ckanext.dataspatial.logic.action.get_connection')
    def test_create_geom_columns_invokes_postgis_api(self, gc, cpc):
        '''Ensure the create_geom_columns action invokes the postgis API

        :param gc: 
        :param cpc: 

        '''
        create_geom_columns({}, {
            u'resource_id': u'a resource',
            u'populate': False,
            u'index': False
            })
        assert_equals(cpc.call_count, 1)
        assert_equals(cpc.call_args_list[0][0][0], u'a resource')

    @patch(u'ckanext.dataspatial.logic.action.create_postgis_index')
    @patch(u'ckanext.dataspatial.logic.action.create_postgis_columns')
    @patch(u'ckanext.dataspatial.logic.action.get_connection')
    def test_create_geom_columns_invokes_postgis_index_api(self, gc, cpc, cpi):
        '''Ensure the create_geom_columns action invokes the postgis index API

        :param gc: 
        :param cpc: 
        :param cpi: 

        '''
        create_geom_columns({}, {
            u'resource_id': u'a resource',
            u'populate': False,
            u'index': True
            })
        assert_equals(cpi.call_count, 1)
        assert_equals(cpi.call_args_list[0][0][0], u'a resource')

    @patch(u'ckanext.dataspatial.logic.action.update_geom_columns')
    @patch(u'ckanext.dataspatial.logic.action.create_postgis_columns')
    @patch(u'ckanext.dataspatial.logic.action.get_connection')
    def test_create_geom_columns_invokes_populate(self, gc, cpc, ugc):
        '''Ensure the create_geom_columns action invokes populate

        :param gc: 
        :param cpc: 
        :param ugc: 

        '''
        dc = {
            u'resource_id': u'a resource',
            u'populate': True,
            u'index': False,
            u'latitude_field': u'latitude',
            u'longitude_field': u'longitude'
            }
        create_geom_columns({}, dc)
        assert_equals(ugc.call_count, 1)
        assert_equals(ugc.call_args_list[0][0][1], dc)

    def test_update_geom_columns_requires_lat_and_long(self):
        '''Check that update_geom_columns raises if lat/long are not defined'''
        assert_raises(toolkit.ValidationError, update_geom_columns, {}, {
            u'resource_id': u'a resource'
            })

    @patch(u'ckanext.dataspatial.logic.action.populate_postgis_columns')
    def test_update_geom_columns_invokes_postgis_api(self, ppc):
        '''Ensure the update_geom_columns action invokes the postgis API

        :param ppc: 

        '''
        update_geom_columns({}, {
            u'resource_id': u'a resource',
            u'latitude_field': u'lat',
            u'longitude_field': u'long'
            })
        assert_equals(ppc.call_count, 1)
        assert_equals(ppc.call_args_list[0][0][0], u'a resource')

    @patch(u'ckanext.dataspatial.logic.action.postgis_query_extent')
    def test_query_extent_invokes_postgis_api(self, pqe):
        '''Ensure that query_extent invokes the postgis API

        :param pqe: 

        '''
        datastore_query_extent({}, {})
        assert_equals(pqe.call_count, 1)

    @patch(u'ckanext.dataspatial.logic.action.solr_query_extent')
    def test_query_extent_invokes_solr_api(self, sqe):
        '''Ensure that query_extent invokes the solr API when configured to do so

        :param sqe: 

        '''
        try:
            config[u'use_datasolr'] = True
            datastore_query_extent({}, {})
            assert_equals(sqe.call_count, 1)
        finally:
            config[u'use_datasolr'] = False
