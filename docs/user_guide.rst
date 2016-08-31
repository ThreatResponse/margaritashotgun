
==========
User Guide
==========

.. contents::

Command Line
************

Common Examples
---------------

See :doc:`the quickstart <quickstart>` for common examples.

Usage
-----

``margaritashotgun`` has man configuration flags which are outlined in detail below.

.. code-block:: bash

   $ margaritashotgun -h
   usage: margaritashotgun [-h] (-c CONFIG | -s SERVER) [-P PORT] [-u USERNAME]
                           [-m MODULE] [-p PASSWORD] [-k KEY] [-f FILENAME]
                           [--repository] [--repository-url REPOSITORY_URL]
                           [-w WORKERS] [-v] [-b BUCKET | -o OUTPUT_DIR]
                           [-d LOG_DIR] [--log_prefix LOG_PREFIX]
   
   Remote memory aquisition wrapper for LiME
   
   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           path to config.yml
     -s SERVER, --server SERVER
                           hostname or ip of target server
     -b BUCKET, --bucket BUCKET
                           memory dump output bucket
     -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                           memory dump output directory
   
     -P PORT, --port PORT  ssh port on remote server
     -u USERNAME, --username USERNAME
                           username for ssh connection
     -m MODULE, --module MODULE
                           path to kernel lime kernel module
     -p PASSWORD, --password PASSWORD
                           password for user or encrypted keyfile
     -k KEY, --key KEY     path to rsa key for ssh connection
     -f FILENAME, --filename FILENAME
                           memory dump filename
     --repository          enable automatic kernel module downloads
     --repository-url REPOSITORY_URL
                           repository url
     -w WORKERS, --workers WORKERS
                           number of workers to run in parallel,default: auto
                           acceptable values are(INTEGER | "auto")
     -v, --verbose         log debug messages
   
     -d LOG_DIR, --log_dir LOG_DIR
                           log directory
     --log_prefix LOG_PREFIX
                          log file prefix

Config
------

TODO

Server
------

TODO

Bucket
------

TODO

Output_Dir
----------

TODO

Port
----

TODO

Username
--------

TODO

Module
------

TODO

Password
--------

TODO

Key
---

TODO

Filename
--------

TODO

Repository
----------

TODO

Repository_Url
--------------

TODO

Workers
-------

TODO

Verbose
-------

TODO

Log_Dir
-------

TODO

Log_Prefix
----------

TODO


Configuration File
******************

TODO

Managing Credentials
********************

TODO

Wrapping Margarita Shotgun
**************************

Margarita Shotgun can be driven by another program when included as a python module.
A structure similar to the configuration file is must be passed to the margaritashotgun client.

Example
-------

.. code-block:: python

   >>> import margaritashotgun
   >>> config = dict(aws dict(bucket = 'case-bucket'),
   ...               hosts = [ dict(addr = '10.10.12.10',
   ...                              port = 22,
   ...                              username = 'ec2-user',
   ...                              key = '/path/to/private-key') ]
   ...               workers = 'auto',
   ...               logging = dict(log_dir = 'logs/',
   ...                              prefix = 'casenumber-10.10.12.10'),
   ...               repository = dict(enabled = true,
   ...                                 url = 'your-custom-kernel-module-repo.io'))
   ...
   >>> capture_client = margaritashotgun.client(name='mem-capture', config=config,
   ...                                          library=True, verbose=False)
   ...
   >>> response = capture_client.run()
   >>> print(response)
   {'total':1,'failed':[],'completed':['10.10.12.10']}

Note that calling ``capture_client.run()`` is a blocking operation.

Configuration
-------------

TODO

Real world implementation
-------------------------

An example of wrapping margaritashotgun is the project `aws ir <https://github.com/ThreatResponse/aws_ir>`_ availible on github.
