import ckan.plugins.toolkit as toolkit

from ckanext.dataspatial.config import config
from ckanext.dataspatial.db import get_connection, create_index, index_exists
from ckanext.dataspatial.db import fields_exist, create_geom_column
from ckanext.dataspatial.db import invoke_search_plugins
from ckanext.datastore import db as datastore_db
from ckanext.datastore.helpers import is_single_statement


def has_postgis_columns(resource_id, connection=None):
    """Returns TRUE if the given resource already has postgis columns

    The name of the columns is read from the configuration.

    @param resource_id: Resource to test
    @param connection: Database connection. If None, one will be
        created for this operation.
    @returns: True if the resource database table already has postgis
              columns, False otherwise.
    """
    mercator_field = config['postgis.mercator_field']
    field = config['postgis.field']

    with get_connection(connection) as c:
        return fields_exist(c, resource_id, [field, mercator_field])


def has_postgis_index(resource_id, connection=None):
    """ Returns TRUE if the given resource already has an index on postgis columns

    @param resource_id: The resource to test
    @param connection: Database connection. If None, one will be
        created for this operation.
    @returns: True if the resource database already has the index for the
              postgis columns
    """
    mercator_field = config['postgis.mercator_field']
    field = config['postgis.field']

    exists = True
    with get_connection(connection) as c:
        if not has_postgis_columns(resource_id, c):
            return False
        exists = exists and index_exists(c, resource_id, field)
        exists = exists and index_exists(c, resource_id, mercator_field)
    return exists


def create_postgis_columns(resource_id, connection=None):
    """ Create the PostGIS columns

    The column names are read from the configuration

    @param resource_id: The resource id to create the columns on
    @param connection: Database connection. If None, one will be
        created for this operation.
    """
    mercator_field = config['postgis.mercator_field']
    field = config['postgis.field']

    with get_connection(connection, write=True) as c:
        create_geom_column(c, resource_id, field, 4326)
        create_geom_column(c, resource_id, mercator_field, 3857)


def create_postgis_index(resource_id, connection=None):
    """ Create geospatial index

    The column name to create the index on is read from the configuration

    @param resource_id: The resource to create the index on
    @param connection: Database connection. If None, one will be
        created for this operation.
    """
    mercator_field = config['postgis.mercator_field']
    field = config['postgis.field']

    with get_connection(connection, write=True) as c:
        if not has_postgis_index(resource_id, c):
            create_index(c, resource_id, field)
            create_index(c, resource_id, mercator_field)


def populate_postgis_columns(resource_id, lat_field, long_field,
                             progress=None, connection=None):
    """ Populate the PostGis columns from the give lat & long fields

    @param resource_id: The resource to populate
    @param lat_field: The latitude field to populate from
    @param long_field: The longitude field to populate from
    @param progress: Optionally, a callable invoked at regular interval with
        the number of rows that were updated
    @param connection: Database connection. If None, one will be
        created for this operation.
    """
    mercator_field = config['postgis.mercator_field']
    field = config['postgis.field']

    with get_connection(connection, write=True, raw=True) as c:
        # This is timing out for big datasets (KE EMu), so we're going to break into a batch operation
        # We need two cursors, one for reading; one for writing
        # And the write cursor will be committed every x number of times (incremental_commit_size)
        read_cursor = c.cursor()
        write_cursor = c.cursor()

        # Retrieve all IDs of records that require updating
        # Either: lat field doesn't match that in the geom column
        # OR geom is  null and /lat/lon is populated
        read_sql = """
          SELECT _id
          FROM "{resource_id}"
          WHERE "{lat_field}" <= 90 AND "{lat_field}" >= -90 AND "{long_field}" <= 180 AND "{long_field}" >= -180
            AND (
              ("{geom_field}" IS NULL AND "{lat_field}" IS NOT NULL OR ST_Y("{geom_field}") <> "{lat_field}")
              OR
              ("{geom_field}" IS NULL AND "{long_field}" IS NOT NULL OR ST_X("{geom_field}") <> "{long_field}")
            )
         """.format(
            resource_id=resource_id,
            geom_field=field,
            long_field=long_field,
            lat_field=lat_field
        )

        read_cursor.execute(read_sql)

        count = 0
        incremental_commit_size = 1000

        sql = """
          UPDATE "{resource_id}"
          SET "{geom_field}" = st_setsrid(st_makepoint("{long_field}"::float8, "{lat_field}"::float8), 4326),
              "{mercator_field}" = st_transform(st_setsrid(st_makepoint("{long_field}"::float8, "{lat_field}"::float8), 4326), 3857)
          WHERE _id = %s
         """.format(
            resource_id=resource_id,
            mercator_field=mercator_field,
            geom_field=field,
            long_field=long_field,
            lat_field=lat_field
        )

        while True:
            output = read_cursor.fetchmany(incremental_commit_size)
            if not output:
                break

            for row in output:
                count += 1
                write_cursor.execute(sql,([row[0]]))

            #commit, invoked every incremental commit size
            c.commit()
            if progress:
                progress(count)

        c.commit()


def query_extent(data_dict, connection=None):
    """ Return the spatial query extent of a datastore search

    @param data_dict: Dictionary defining the search
    @returns a dictionary defining:
        {
            total_count: The total number of rows in the query,
            geom_count: The number of rows that have a geom,
            bounds: ((lat min, long min), (lat max, long max)) for the
                  queries rows
    """
    r = toolkit.get_action('datastore_search')({}, data_dict)
    if 'total' not in r or r['total'] == 0:
        return {
            'total_count': 0,
            'geom_count': 0,
            'bounds': None
        }
    result = {
        'total_count': r['total'],
        'bounds': None
    }
    field_types = dict([(f['id'], f['type']) for f in r['fields']])
    field_types['_id'] = 'int'
    # Call plugin to obtain correct where statement
    (ts_query, where_clause, values) = invoke_search_plugins(data_dict, field_types)
    # Prepare and run our query
    query = """
        SELECT COUNT(r) AS count,
               ST_YMIN(ST_EXTENT(r)) AS ymin,
               ST_XMIN(ST_EXTENT(r)) AS xmin,
               ST_YMAX(ST_EXTENT(r)) AS ymax,
               ST_XMAX(ST_EXTENT(r)) AS xmax
        FROM   (
          SELECT "{geom_field}" AS r
          FROM   "{resource_id}" {ts_query}
          {where_clause}
        ) _tilemap_sub
    """.format(
        geom_field=config['postgis.field'],
        resource_id=data_dict['resource_id'],
        where_clause=where_clause,
        ts_query=ts_query
    )
    if not is_single_statement(query):
        raise datastore_db.ValidationError({
            'query': ['Query is not a single statement.']
        })
    with get_connection(connection) as c:
        query_result = c.execute(query, values)
        r = query_result.fetchone()

    result['geom_count'] = r['count']
    if result['geom_count'] > 0:
        result['bounds'] = ((r['ymin'], r['xmin']), (r['ymax'], r['xmax']))
    return result
