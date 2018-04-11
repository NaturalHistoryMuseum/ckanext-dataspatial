#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

import ckanext.dataspatial.lib.postgis as pgs
from ckanext.dataspatial.config import config
from mock import patch
from nose.tools import assert_equals, assert_true


class TestPostGIS(object):
    '''TODO: We cannot currently unit test populate_postgis_columns
        and query_extent because they invoke the db api directly.


    '''

    def setup(self):
        ''' '''
        config[u'postgis.field'] = u'the_field'
        config[u'postgis.mercator_field'] = u'the_mercator'

    @patch(u'ckanext.dataspatial.lib.postgis.create_geom_column')
    @patch(u'ckanext.dataspatial.lib.postgis.get_connection')
    def test_create_postgis_columns_invoked_db(self, gc, cgo):
        '''Test create_postgis_columns invokes the database API as expected

        :param gc: 
        :param cgo: 

        '''
        pgs.create_postgis_columns(u'a_resource')
        assert_equals(cgo.call_count, 2)
        assert_equals(cgo.call_args_list[0][0][1:], (
            u'a_resource', u'the_field', 4326
            ))
        assert_equals(cgo.call_args_list[1][0][1:], (
            u'a_resource', u'the_mercator', 3857
            ))

    @patch(u'ckanext.dataspatial.lib.postgis.create_index')
    @patch(u'ckanext.dataspatial.lib.postgis.get_connection')
    def test_create_postgis_index_invoked_db(self, gc, ci):
        '''

        :param gc: 
        :param ci: 

        '''
        pgs.create_postgis_index(u'a_resource')
        assert_equals(ci.call_count, 2)
        assert_equals(ci.call_args_list[0][0][1:], (
            u'a_resource', u'the_field'
            ))
        assert_equals(ci.call_args_list[1][0][1:], (
            u'a_resource', u'the_mercator'
            ))

    @patch(u'ckanext.dataspatial.lib.postgis.fields_exist')
    @patch(u'ckanext.dataspatial.lib.postgis.get_connection')
    def test_has_postgis_columns_invoked_db(self, gc, fe):
        '''

        :param gc: 
        :param fe: 

        '''
        fe.return_value = True
        r = pgs.has_postgis_columns(u'a_resource')
        assert_true(r)
        assert_equals(fe.call_count, 1)
        assert_equals(fe.call_args_list[0][0][1:], (
            u'a_resource', [u'the_field', u'the_mercator']
            ))

    @patch(u'ckanext.dataspatial.lib.postgis.has_postgis_columns')
    @patch(u'ckanext.dataspatial.lib.postgis.index_exists')
    @patch(u'ckanext.dataspatial.lib.postgis.get_connection')
    def test_has_postgis_index_invoked_db(self, gc, ie, hpc):
        '''

        :param gc: 
        :param ie: 
        :param hpc: 

        '''
        ie.return_value = True
        hpc.return_value = True
        r = pgs.has_postgis_index(u'a_resource')
        assert_true(r)
        assert_equals(ie.call_count, 2)
        assert_equals(ie.call_args_list[0][0][1:], (
            u'a_resource', u'the_field'
            ))
        assert_equals(ie.call_args_list[1][0][1:], (
            u'a_resource', u'the_mercator'
            ))
