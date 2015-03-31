from setuptools import setup, find_packages

with open('ckanext/dataspatial/version.py') as f:
    exec(f.read())

setup(
    name='ckanext-dataspatial',
    version=__version__,
    description='Ckan extension to provide geospatial awareness of datastore datasets',
    url='http://github.com/NaturalHistoryMuseum/ckanext-dataspatial',
    packages=find_packages(exclude='tests'),
	entry_points="""
        [ckan.plugins]
            dataspatial = ckanext.dataspatial.plugin:DataSpatialPlugin
        [paste.paster_command]
            dataspatial = ckanext.dataspatial.commands.dataspatial:DataSpatialCommand
	"""
)
