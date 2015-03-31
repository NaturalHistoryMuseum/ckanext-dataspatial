from ckanext.dataspatial.config import config
from ckanext.dataspatial.lib.postgis import query_extent as postgis_query_extent
from ckanext.dataspatial.lib.solr import query_extent as solr_query_extent


def datastore_query_extent(context, data_dict):
    """ Return the geospatial extent of a given datastore queries.

    The arguments as per `datastore_search`, and the return value defines:
    {
        'total_count': Total number of rows matching the query,
        'geom_count': Number of rows matching the query that have geospatial
                      information
        'bounds': ((lat min, long min), (lat max, long max)) for the
                  queries rows
    }

    @param context: Current context
    @data_dict: Request arguments, as per datastore_search
    """
    if config['use_datasolr']:
        return solr_query_extent(data_dict)
    else:
        return postgis_query_extent(data_dict)
