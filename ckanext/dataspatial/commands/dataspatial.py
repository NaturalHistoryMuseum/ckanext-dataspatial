#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-dataspatial
# Created by the Natural History Museum in London, UK

import logging

from ckanext.dataspatial.lib.postgis import (create_postgis_columns,
                                             create_postgis_index,
                                             populate_postgis_columns)

from ckan.plugins import toolkit

log = logging.getLogger(u'ckan')


class DataSpatialCommand(toolkit.CkanCommand):
    '''Create & populate postgis spatial columns'''
    usage = u'(create-columns|create-index|populate-columns) resource_id'
    summary = u'Create & populate postgis spatial columns on datasets.'
    max_args = 2
    min_args = 2

    def __init__(self, name):
        super(DataSpatialCommand, self).__init__(name)
        self.parser.add_option(
            u'-l', u'--latitude_field',
            help=u'The latitude field to populate the columns from. Required '
                 + u'for update-columns'
            )
        self.parser.add_option(
            u'-g', u'--longitude_field',
            help=u'The longitude field to populate the columns from. Required '
                 + u'for populate-columns'
            )

    def command(self):
        '''Parse command line arguments and call appropriate method.'''
        # Additional validation
        errors = []
        if self.args[0] not in [u'create-columns', u'create-index', u'populate-columns']:
            errors.append(
                u'Please specify one of create-columns, create-index or '
                u'populate-columns')
        elif self.args[0] == u'populate-columns' and not (
                self.options.latitude_field and self.options.longitude_field):
            errors.append(
                u'Latitude and longitude fields are required for populate-columns')
        if len(errors):
            print u'\n'.join(errors)
            return

        # Load configuration
        self._load_config()

        # Invoke necessary commands
        if self.args[0] == u'create-columns':
            print u'Creating postgis columns on {}'.format(self.args[1])
            create_postgis_columns(self.args[1])
        elif self.args[0] == u'create-index':
            print u'Creating index on postgis columns on {}'.format(self.args[1])
            create_postgis_index(self.args[1])
        elif self.args[0] == u'populate-columns':
            print u'Populating postgis columns on {}'.format(self.args[1])
            populate_postgis_columns(
                self.args[1], self.options.latitude_field,
                self.options.longitude_field,
                progress=self._populate_progress_counter
                )
        print u'Done.'

    def _populate_progress_counter(self, count):
        '''

        :param count: 

        '''
        print u'Updated {} rows'.format(count)
