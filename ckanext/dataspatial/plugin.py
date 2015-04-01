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
        config_items = config.keys()
        for long_name in ckan_config:
            if not long_name.startswith(prefix):
                continue
            name = long_name[len(prefix):]
            if name in config_items:
                config[name] = ckan_config[long_name]
            else:
                raise p.toolkit.ValidationError({
                    long_name: 'Unknown configuration setting'
                })
        if config['query_extent'] not in ['postgis', 'solr']:
            raise p.toolkit.ValidationError({
                'dataspatial.query_extent': 'Should be either of postgis or solr'
            })

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

    ## IDataSolr
    def datasolr_validate(self, context, data_dict, fields_types):
        return self.datastore_validate(context, data_dict, fields_types)

    def datasolr_search(self, context, data_dict, fields_types, query_dict):
        try:
            tmgeom = data_dict['filters']['_tmgeom']
        except KeyError:
            return query_dict
        field_name = config['solr.index_field']
        for geom in tmgeom:
            query_dict['q'][0].append(
                '{}:"Intersects({{}}) distErrPct=0"'.format(field_name)
            )
            query_dict['q'][1].append(geom)

        return query_dict
