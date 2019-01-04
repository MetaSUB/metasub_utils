=================
MetaSUB Utilities
=================


.. image:: https://img.shields.io/pypi/v/metasub_utils.svg
        :target: https://pypi.python.org/pypi/metasub_utils

.. image:: https://circleci.com/gh/MetaSUB/metasub_utils.svg?style=svg
        :target: https://circleci.com/gh/MetaSUB/metasub_utils

.. image:: https://www.codefactor.io/Content/badges/A.svg
        :target: https://www.codefactor.io/repository/github/metasub/metasub_utils

Utilities for the MetaSUB Consortium. Free software: MIT license.


Features
--------

A collection of utilites to manage the MetaSUB project.

- Athena is a collection of tools to manage data on the Weill-Cornell ICB Compute Cluster
- Bridges is a collection of tools to manage data on the XSEDE Bridges Compute Cluster
- Data Packet contains scripts for building MetaSUB data packets
- Hudson Alpha contains tools for downloading raw sequence data from Hudson Alpha
- Metadata provides access to the MetaSUB Metadata_
- Metagenscope is a set of utilites to upload data to metagenscope_
- Wasabi uploads and downloads data from Wasabi Hot Storage, an S3 clone
- Zurich uploads and downloads data from the Zurich MetaSUB SFTP server 


Installation
------------

You need to be using py3 to install this package.

Install from PyPi

.. code-block:: bash

    pip install metasub_utils


Install from source.

.. code-block:: bash

    git clone git@github.com:MetaSUB/metasub_utils.git
    cd metasub_utils
    python setup.py install


Downloading Data From Wasabi
----------------------------

To download data or assemblies from wasabi you will need API credentials. Please contact David Danko (dcd3001@med.cornell.edu) to acquire these keys.

Wasabi is a clone of amazon S3. To use Wasabi you will need to install the AWS-CLI_

Once you have installed the aws command line tool you need to configure an account.

.. code-block:: bash

    $ aws configure --profile wasabi
    AWS Access Key ID [None]: `your access key`
    AWS Secret Access Key [None]: `your secret key`
    Default region name [None]: 
    Default output format [None]:
    
Once your account is configured you can use this utility package to download files. The following commands will be most useful.

.. code-block:: bash

    $ metasub wasabi download-contigs --help
    $ metasub wasabi download-raw-reads --help
    
Note that all download commands dryrun by default. You will need to add the `--wetrun` flag to actually download data.

To download data from a specific city run

.. code-block:: bash

    $ metasub wasabi download-raw-reads --wetrun --city-name <city_name>


Changelog
---------

v0.4.0
- Added a metadata CLI/API to list samples from a particular city
- Added a wasabi CLI/API to list raw reads with a city-specific option
- Added a wasabi CLI/API to download raw reads with a city-specific option


Credits
---------

This package is structured as a set of microlibraries_

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _metadata: https://github.com/MetaSUB/MetaSUB-metadata
.. _metagenscope: https://www.metagenscope.com/
.. _microlibraries: https://blog.shazam.com/python-microlibs-5be9461ad979
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _AWS-CLI: https://docs.aws.amazon.com/cli/latest/userguide/installing.html
