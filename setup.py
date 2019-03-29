"""Macro module for MetaSUB Utilites.
Based on: https://blog.shazam.com/python-microlibs-5be9461ad979
"""

import os
from six import iteritems
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call


PACKAGE_NAME = 'metasub_utils'


SOURCES = {
    'metasub_utils.athena': 'metasub_utils/athena',
    'metasub_utils.bridges': 'metasub_utils/bridges',
    'metasub_utils.hudson_alpha': 'metasub_utils/hudson_alpha',
    'metasub_utils.metadata==0.3.1': 'metasub_utils/metadata',
    'metasub_utils.metagenscope': 'metasub_utils/metagenscope',
    'metasub_utils.wasabi==0.5.4': 'metasub_utils/wasabi',
    'metasub_utils.zurich': 'metasub_utils/zurich',
    'metasub_utils.packet_parse==0.1.0': 'metasub_utils/packet_parse',
}


def install_microlibs(sources, develop=False):
    """ Use pip to install all microlibraries.  """
    print('Installing all microlibs in {} mode'.format(
              'development' if develop else 'normal'))
    working_dir = os.getcwd()
    for name, path in iteritems(sources):
        try:
            os.chdir(os.path.join(working_dir, path))
            if develop:
                check_call(["python", '-m', 'pip', 'install', '-e', '.'])
            else:
                check_call(["python", '-m', 'pip', 'install', '.'])
        except Exception as e:
            print('Something went wrong installing', name)
            print(e)
        finally:
            os.chdir(working_dir)


class DevelopCmd(develop):
    """ Add custom steps for the develop command """
    def run(self):
        install_microlibs(SOURCES, develop=True)
        develop.run(self)


class InstallCmd(install):
    """ Add custom steps for the install command """
    def run(self):
        install_microlibs(SOURCES, develop=False)
        install.run(self)


setup(
    name=PACKAGE_NAME,
    version='0.5.5',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    description='Utility functions for the MetaSUB Consortium',
    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'future',
        'six',
    ] + list(SOURCES.keys()),
    entry_points={
        'console_scripts': [
            'metasub=metasub_utils.cli:main'
        ]
    },
    cmdclass={
        'install': InstallCmd,
        'develop': DevelopCmd,
    },
    packages=[PACKAGE_NAME],
    package_dir={PACKAGE_NAME: 'metasub_utils'},
)
