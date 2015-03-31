import ckan.lib.cli as cli

import logging

from ckanext.dataspatial.lib.postgis import create_postgis_columns
from ckanext.dataspatial.lib.postgis import create_postgis_index
from ckanext.dataspatial.lib.postgis import populate_postgis_columns

log = logging.getLogger('ckan')


class DataSpatialCommand(cli.CkanCommand):
    """ Create & populate postgis spatial columns """
    usage = '(create-columns|create-index|populate-columns) resource_id'
    summary = 'Create & populate postgis spatial columns on datasets.'
    max_args = 2
    min_args = 2

    def __init__(self, name):
        super(DataSpatialCommand, self).__init__(name)
        self.parser.add_option(
            '-l', '--latitude_field',
            help='The latitude field to populate the columns from. Required '
                +'for update-columns'
        )
        self.parser.add_option(
            '-g', '--longitude_field',
            help='The longitude field to populate the columns from. Required '
                +'for populate-columns'
        )

    def command(self):
        """ Parse command line arguments and call appropriate method. """
        # Additional validation
        errors = []
        if self.args[0] not in ['create-columns', 'create-index', 'populate-columns']:
            errors.append('Please specify one of create-columns, create-index or populate-columns')
        elif self.args[0] == 'populate-columns' and not (
                self.options.latitude_field and self.options.longitude_field):
            errors.append('Latitude and longitude fields are required for populate-columns')
        if len(errors):
            print "\n".join(errors)
            return

        # Load configuration
        self._load_config()

        # Invoke necessary commands
        if self.args[0] == 'create-columns':
            print "Creating postgis columns on {}".format(self.args[1])
            create_postgis_columns(self.args[1])
        elif self.args[0] == 'create-index':
            print "Creating index on postgis columns on {}".format(self.args[1])
            create_postgis_index(self.args[1])
        elif self.args[0] == 'populate-columns':
            print "Populating postgis columns on {}".format(self.args[1])
            populate_postgis_columns(
                self.args[1], self.options.latitude_field,
                self.options.longitude_field,
                progress=self._populate_progress_counter
            )
        print "Done."

    def _populate_progress_counter(self, count):
        print 'Updated {} rows'.format(count)
