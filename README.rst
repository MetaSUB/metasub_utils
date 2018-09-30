=================
MetaSUB Utilities
=================


.. image:: https://img.shields.io/pypi/v/metasub_utils.svg
        :target: https://pypi.python.org/pypi/metasub_utils

.. image:: https://pyup.io/repos/github/dcdanko/metasub_utils/shield.svg
     :target: https://pyup.io/repos/github/dcdanko/metasub_utils/
     :alt: Updates


Utilities for the MetaSUB Consortium


* Free software: MIT license


Features
--------

A collection of utilites to manage the MetaSUB project.

Most of the tools in this package involve uploading or downloading data.

.. code-block:: bash

    pip install metasub_utils


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
    $ metasub wasabi download-unassembled-data --help
    
Note that all download commands dryrun by default. You will need to add the `--wetrun` flag to actually download data.

    


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _AWS-CLI: https://docs.aws.amazon.com/cli/latest/userguide/installing.html
