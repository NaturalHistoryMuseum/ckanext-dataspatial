import ckan.plugins as p
import re

from ckanext.dataspatial.logic.action import create_geom_columns, update_geom_columns
from ckanext.dataspatial.logic.search import datastore_query_extent
from ckanext.dataspatial.config import config
from ckanext.datastore.interfaces import IDatastore
try:
    from ckanext.datasolr.interfaces import IDataSolr
except ImportError:
    pass


class DataSpatialPlugin(p.SingletonPlugin):
    p.implements(p.interfaces.IConfigurable)
    p.implements(p.interfaces.IActions)
    p.implements(IDatastore)
    try:
        p.implements(IDataSolr)
    except NameError:
        pass

    # IConfigurable
    def configure(self, ckan_config):
        prefix = 'dataspatial.'
        config_items = ['solr.field', 'postgis.field', 'postgis.mercator_field']
        bool_config_items = ['use_datasolr']
        for long_name in ckan_config:
            if not long_name.startswith(prefix):
                continue
            name = long_name[len(prefix):]
            if name in config_items:
                config[name] = ckan_config[long_name]
            elif name in bool_config_items:
                config[name] = ckan_config[long_name].lower() in ['yes', 'ok', 'true', '1']


    # IActions
    def get_actions(self):
        return {
            'create_geom_columns': create_geom_columns,
            'update_geom_columns': update_geom_columns,
            'datastore_query_extent': datastore_query_extent
        }

    # IDatastore
    def datastore_validate(self, context, data_dict, all_field_ids):
        # Validate geom fields
        if 'fields' in data_dict:
            geom_fields = [config['postgis.field'], config['postgis.mercator_field']]
            data_dict['fields'] = [f for f in data_dict['fields'] if f not in geom_fields]
        # Validate geom filters
        try:
            # We'll just check that this *looks* like a WKT, in which case we will trust 
            # it's valid. Worst case the query will fail, which is handled gracefully anyway.
            for i, v in enumerate(data_dict['filters']['_tmgeom']):
                if re.search('^\s*(POLYGON|MULTIPOLYGON)\s*\([-+0-9,(). ]+\)\s*$', v):
                    del data_dict['filters']['_tmgeom'][i]
            if len(data_dict['filters']['_tmgeom']) == 0:
                del data_dict['filters']['_tmgeom']
        except KeyError:
            pass
        except TypeError:
            pass

        return data_dict

    def datastore_search(self, context, data_dict, all_field_ids, query_dict):
        try:
            tmgeom = data_dict['filters']['_tmgeom']
        except KeyError:
            return query_dict

        clauses = []
        field_name = config['postgis.field']
        for geom in tmgeom:
            clauses.append((
                "ST_Intersects(\"{field}\", ST_GeomFromText(%s, 4326))".format(field=field_name),
                geom
            ))

        query_dict['where'] += clauses
        return query_dict

    def datastore_delete(self, context, data_dict, all_field_ids, query_dict):
        return query_dict

    # IDataSolr
    def datasolr_validate(self, context, data_dict, field_types):
        """ Validates the input request.

        This is the main validator, which will remove all known fields
        from fields, sort, q as well as all other accepted input parameters.
        """
        return data_dict

    def datasolr_search(self, context, data_dict, field_types, query_dict):
        """ Build the solr search """
        return dict(query_dict.items() + solr_args.items())
