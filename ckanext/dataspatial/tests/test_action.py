import ckan.plugins.toolkit as toolkit
from ckanext.dataspatial.config import config
from ckanext.dataspatial.logic.action import create_geom_columns
from ckanext.dataspatial.logic.action import update_geom_columns
from ckanext.dataspatial.logic.action import get_query_extent
from mock import patch
from nose.tools import assert_equals, assert_raises


class TestActions(object):
    def test_create_geom_columns_requires_resource_id(self):
        """ Ensure the create_geom_columns action raises if resource_id is not
             provided. """
        assert_raises(toolkit.ValidationError, create_geom_columns, {}, {})

    @patch('ckanext.dataspatial.logic.action.create_postgis_columns')
    @patch('ckanext.dataspatial.logic.action.get_connection')
    def test_create_geom_columns_invokes_postgis_api(self, gc, cpc):
        """ Ensure the create_geom_columns action invokes the postgis API """
        create_geom_columns({}, {
            'resource_id': 'a resource',
            'populate': False,
            'index': False
        })
        assert_equals(cpc.call_count, 1)
        assert_equals(cpc.call_args_list[0][0][0], 'a resource')

    @patch('ckanext.dataspatial.logic.action.create_postgis_index')
    @patch('ckanext.dataspatial.logic.action.create_postgis_columns')
    @patch('ckanext.dataspatial.logic.action.get_connection')
    def test_create_geom_columns_invokes_postgis_index_api(self, gc, cpc, cpi):
        """ Ensure the create_geom_columns action invokes the postgis index API """
        create_geom_columns({}, {
            'resource_id': 'a resource',
            'populate': False,
            'index': True
        })
        assert_equals(cpi.call_count, 1)
        assert_equals(cpi.call_args_list[0][0][0], 'a resource')


    @patch('ckanext.dataspatial.logic.action.update_geom_columns')
    @patch('ckanext.dataspatial.logic.action.create_postgis_columns')
    @patch('ckanext.dataspatial.logic.action.get_connection')
    def test_create_geom_columns_invokes_populate(self, gc, cpc, ugc):
        """ Ensure the create_geom_columns action invokes populate """
        dc = {
            'resource_id': 'a resource',
            'populate': True,
            'index': False,
            'latitude_field': 'latitude',
            'longitude_field': 'longitude'
        }
        create_geom_columns({}, dc)
        assert_equals(ugc.call_count, 1)
        assert_equals(ugc.call_args_list[0][0][1], dc)

    def test_update_geom_columns_requires_lat_and_long(self):
        """ Check that update_geom_columns raises if lat/long are not defined """
        assert_raises(toolkit.ValidationError, update_geom_columns, {}, {
            'resource_id': 'a resource'
        })

    @patch('ckanext.dataspatial.logic.action.populate_postgis_columns')
    def test_update_geom_columns_invokes_postgis_api(self, ppc):
        """ Ensure the update_geom_columns action invokes the postgis API """
        update_geom_columns({}, {
            'resource_id': 'a resource',
            'latitude_field': 'lat',
            'longitude_field': 'long'
        })
        assert_equals(ppc.call_count, 1)
        assert_equals(ppc.call_args_list[0][0][0], 'a resource')

    @patch('ckanext.dataspatial.logic.action.postgis_query_extent')
    def test_query_extent_invokes_postgis_api(self, pqe):
        """ Ensure that query_extent invokes the postgis API """
        get_query_extent({}, {})
        assert_equals(pqe.call_count, 1)

    @patch('ckanext.dataspatial.logic.action.solr_query_extent')
    def test_query_extent_invokes_solr_api(self, sqe):
        """ Ensure that query_extent invokes the solr API when configured to do so """
        try:
            config['use_datasolr'] = True
            get_query_extent({}, {})
            assert_equals(sqe.call_count, 1)
        finally:
            config['use_datasolr'] = False