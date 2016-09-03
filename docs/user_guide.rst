
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

The ``-c`` and ``--config`` flags accept a relative or absolute path to a yml config file.
The structure of this file is outlided in the ``Configuration`` section below.

Server
------

The ``-s`` and ``--server`` flags specify the server being targeted for memory capture.
A DNS record or IP address are valid inputs.

Bucket
------

The ``-b`` and ``--bucket`` flags specify the destination bucket when dumping memory to s3.
This flag cannot be used in conjunction wth ``-o`` or ``--output_dir``.

Output_Dir
----------

The ``-o`` and ``--output_dir`` flags specify the destination folder when dumping memory to the local filesystem.
This flag  cannot be used in conjunction with ``-b`` or ``--bucket``.

Port
----

The ``-p`` and ``--port`` flags specify the port that ssh is running on the remote server specified by ``-s`` or ``--server``.
This flag is optional and port ``22`` will be assumed if no value is provided.

Username
--------

The ``-u`` and ``--username`` flags specify the user account to authenticate with when connecting to the remote server specified by ``-s`` or ``--server``.

Module
------

The ``-m`` and ``--module`` flags accept a relative or absolute path to a `LiME <https://github.com/504ensicsLabs/LiME>`__ kernel module.
This flag is required if no kernel module repository is enabled with the ``--repository`` flag.

Password
--------

The ``-p`` and ``--password`` flags specify the password used for authentication with connection to the remote server specified by ``-s`` or ``--server``.
When used in conjuction with the ``-k`` or ``--key`` flags this password will be used to unlock a protected private key file.

Key
---

The ``-k`` and ``--key`` flags accept a relative or absolute path to a a private key file used for authentication when connecting to the server specified by ``-s`` or ``-server``.
If the private key file specified is password protected use the ``-p`` or ``--password`` flags to specify the password that unlocks the private key.

Filename
--------

The ``-f`` and ``--filename`` flags specify the name of the file memory will be saved to when dumping to the local filesystem.
The file will be saved to the local directory unless the ``-o`` or ``--output_dir`` options are configured.

Repository
----------

The ``--repository`` flag enables automatic kernel module resolution via the repository configured with ``--repository-url``.
Margaritashotgun will not query any repositories unless explicitly enabled with the ``--repository`` flag.

Repository_Url
--------------

The ``--repository-url`` flag specifies where to search for kernel modules.  The default public repository provided by `Threat Response <http://www.threatresponse.cloud/>`__ is availible at ``https://threatresponse-lime-modules.s3.amazonaws.com``

Workers
-------

The ``-w`` and ``--workers`` flags specify how many worker processes will be spawned to process memory captures in parallel.
The default value for this flag is ``auto`` which will spawn a process per remote host up to the number of cpu cores on the local system.
Integer values can be provided instead of the ``auto`` keyword.
Eg. ``--workers 3`` will process 3 memory captures simultaneously.

Verbose
-------

The ``-v`` and ``--verbose`` flags enable debug logging, including each command executed on remote hosts as a part of the memory capture process.

Log_Dir
-------

The ``-d`` and ``--log_dir`` flags specify the directory in which to log files will be saved during memory capture.

Log_Prefix
----------

The ``--log_prefix`` flag allows a custom case number to be prepended onto log files for easy identification.


Configuration File
******************

Example configuration files are availible in the `repository <https://github.com/ThreatResponse/margaritashotgun/tree/master/conf>`__.
More documentation about the configuration file format is in the works.

Managing AWS Credentials
************************

Margaritashotgun does not support explicitly declaring aws credentials.  Currently the only way to interact with S3 is by configuring an `aws profile <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html>`__.
A feature is planned to allow selecting a profile other than the ``default`` profile.  Until that feature is completed the ``default`` profile must be used.

Wrapping Margarita Shotgun
**************************

Margarita Shotgun can be driven by another program when included as a python module.
The configuration object passed to the margaritashotgun client must have the exact structure of the configuration file outlined above.

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

Real world implementation
-------------------------

An example of wrapping margaritashotgun is the project `aws ir <https://github.com/ThreatResponse/aws_ir>`_ availible on github.
