from setuptools import setup

microlib_name = 'pangea_modules.ags'

requirements = [
    'pangea_modules.base',
    'pangea_modules.microbe_census_data',
    'mongoengine',
]

setup(
    name=microlib_name,
    version='0.1.2',
    author='Longtail Biotech',
    author_email='dev@longtailbio.com',
    description=('Average Genome Size display the distribution of average '
                 'genome sizes for different metadata attributes.'),
    license='Restricted',
    classifiers=[
        'Private :: Do Not Upload to pypi server',
    ],
    namespace_packages=['pangea_modules'],
    packages=[microlib_name],
    install_requires=requirements,
)
