import copy
from ckan.plugins import toolkit
from ckanext.dataspatial.config import config


def query_extent(data_dict):
    """ Return the spatial query extent of a datastore search

    @param data_dict: Dictionary defining the search
    @returns a dictionary defining:
        {
            total_count: The total number of rows in the query,
            geom_count: The number of rows that have a geom,
            bounds: ((lat min, long min), (lat max, long max)) for the
                  queries rows
        }
    """
    lat_field = config['solr.latitude_field']
    long_field = config['solr.longitude_field']
    result = {
        'total_count': 0,
        'geom_count': 0,
        'bounds': None
    }
    data_dict = copy.deepcopy(data_dict)
    data_dict['offset'] = 0
    data_dict['limit'] = 1
    data_dict['fields'] = ['_id']
    r = toolkit.get_action('datastore_solr_search')({}, data_dict)
    if r['total'] == 0:
        return result
    result['total_count'] = r['total']
    data_dict['solr_stats_fields'] = [lat_field, long_field]
    if 'filters' not in data_dict:
        data_dict['filters'] = {}
    data_dict['filters']['_solr_not_empty'] = [lat_field, long_field]
    r = toolkit.get_action('datastore_solr_search')({}, data_dict)
    if r['total'] == 0:
        return result
    result['geom_count'] = r['total']
    bounds = [[0, 0], [0, 0]]
    for field_def in r['fields']:
        if field_def['id'] == lat_field:
            bounds[0][0] = field_def['min']
            bounds[1][0] = field_def['max']
        elif field_def['id'] == long_field:
            bounds[0][1] = field_def['min']
            bounds[1][1] = field_def['max']
    result['bounds'] = (
        tuple(bounds[0]), tuple(bounds[1])
    )
    return result
