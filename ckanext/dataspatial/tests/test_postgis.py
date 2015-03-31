import ckanext.dataspatial.lib.postgis as pgs

from mock import patch
from ckanext.dataspatial.config import config
from nose.tools import assert_true, assert_equals


class TestPostGIS(object):
    """ TODO: We cannot currently unit test populate_postgis_columns
        and query_extent because they invoke the db api directly.
    """
    def setup(self):
        config['postgis.field'] = 'the_field'
        config['postgis.mercator_field'] = 'the_mercator'

    @patch('ckanext.dataspatial.lib.postgis.create_geom_column')
    @patch('ckanext.dataspatial.lib.postgis.get_connection')
    def test_create_postgis_columns_invoked_db(self, gc, cgo):
        """ Test create_postgis_columns invokes the database API as expected """
        pgs.create_postgis_columns('a_resource')
        assert_equals(cgo.call_count, 2)
        assert_equals(cgo.call_args_list[0][0][1:], (
            'a_resource', 'the_field', 4326
        ))
        assert_equals(cgo.call_args_list[1][0][1:], (
            'a_resource', 'the_mercator', 3857
        ))

    @patch('ckanext.dataspatial.lib.postgis.create_index')
    @patch('ckanext.dataspatial.lib.postgis.get_connection')
    def test_create_postgis_index_invoked_db(self, gc, ci):
        pgs.create_postgis_index('a_resource')
        assert_equals(ci.call_count, 2)
        assert_equals(ci.call_args_list[0][0][1:], (
            'a_resource', 'the_field'
        ))
        assert_equals(ci.call_args_list[1][0][1:], (
            'a_resource', 'the_mercator'
        ))


    @patch('ckanext.dataspatial.lib.postgis.fields_exist')
    @patch('ckanext.dataspatial.lib.postgis.get_connection')
    def test_has_postgis_columns_invoked_db(self, gc, fe):
        fe.return_value = True
        r = pgs.has_postgis_columns('a_resource')
        assert_true(r)
        assert_equals(fe.call_count, 1)
        assert_equals(fe.call_args_list[0][0][1:], (
            'a_resource', ['the_field', 'the_mercator']
        ))


    @patch('ckanext.dataspatial.lib.postgis.has_postgis_columns')
    @patch('ckanext.dataspatial.lib.postgis.index_exists')
    @patch('ckanext.dataspatial.lib.postgis.get_connection')
    def test_has_postgis_index_invoked_db(self, gc, ie, hpc):
        ie.return_value = True
        hpc.return_value = True
        r = pgs.has_postgis_index('a_resource')
        assert_true(r)
        assert_equals(ie.call_count, 2)
        assert_equals(ie.call_args_list[0][0][1:], (
            'a_resource', 'the_field'
        ))
        assert_equals(ie.call_args_list[1][0][1:], (
            'a_resource', 'the_mercator'
        ))
