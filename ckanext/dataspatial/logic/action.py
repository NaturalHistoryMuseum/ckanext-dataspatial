import ckan.plugins.toolkit as toolkit

from ckanext.dataspatial.config import config
from ckanext.dataspatial.lib.postgis import create_postgis_columns
from ckanext.dataspatial.lib.postgis import create_postgis_index
from ckanext.dataspatial.lib.postgis import populate_postgis_columns
from ckanext.dataspatial.lib.postgis import query_extent as postgis_query_extent
from ckanext.dataspatial.lib.solr import query_extent as solr_query_extent
from ckanext.dataspatial.db import get_connection


def create_geom_columns(context, data_dict):
    """Add geom column to the given resource, and optionally populate them.

    @param context: Current context
    @param data_dict: Parameters:
      - resource_id: The resource for which to create geom columns; REQUIRED
      - latitude_field: The existing latitude field in the column, optional unless populate is true
      - longitude_field: The existing longitude field in the column, optional unless populate is true
      - populate: If true then pre-populate the geom fields using the latitude
                  and longitude fields. Defaults to true.
      - index: If true then create an index on the created columns.
               Defaults to true.
    """
    try:
        resource_id = data_dict['resource_id']
    except KeyError:
        raise toolkit.ValidationError({
            'resource_id': 'A Resource id is required'
        })
    if 'populate' in data_dict:
        populate = data_dict['populate']
    else:
        populate = True
    if 'index' in data_dict:
        index = data_dict['index']
    else:
        index = True

    with get_connection(write=True) as connection:
        create_postgis_columns(resource_id, connection)
        if index:
            create_postgis_index(resource_id, connection)

    if populate:
        update_geom_columns(context, data_dict)


def update_geom_columns(context, data_dict):
    """Repopulate the given geom columns

    @param context: Current context
    @param data_dict: Parameters:
      - resource_id: The resource to populate; REQUIRED
      - latitude_field: The existing latitude field in the column, REQUIRED
      - longitude_field: The existing longitude field in the column, REQUIRED
    """
    try:
        resource_id = data_dict['resource_id']
        lat_field = data_dict['latitude_field']
        long_field = data_dict['longitude_field']
    except KeyError:
        raise toolkit.ValidationError('Missing required field')

    populate_postgis_columns(resource_id, lat_field, long_field)

