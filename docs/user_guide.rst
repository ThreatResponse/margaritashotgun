
==========
User Guide
==========

Command Line
************

.. note::

   See the :doc:`quickstart <quickstart>` for common examples.

Usage
-----

Run ``margaritashotgun -h`` at the command line, detailed information on flags is below.

Quick Reference
---------------

+---------------------------+--------------------------+-------------------------------------------+
| Flag                      | Use                      | Notes                                     |
+---------------------------+--------------------------+-------------------------------------------+
| ``--config``              | path to config file      | See the **Configuration File** section    |
+---------------------------+--------------------------+-------------------------------------------+
| ``--server``              | ip of remote server      | DNS records may also be used              |
+---------------------------+--------------------------+-------------------------------------------+
| ``--version``             | print version info       |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--bucket``              | output S3 bucket         | Incommpatible with ``-o``                 |
+---------------------------+--------------------------+-------------------------------------------+
| ``--output-dir``          | local output folder      | Incompatible with ``-b``                  |
+---------------------------+--------------------------+-------------------------------------------+
| ``--port``                | ssh port                 | ``22`` is used unless specified           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--username``            | ssh username             | Username for ssh authentication           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--module``              | lime kernel module       | Required if no repository is enabled      |
+---------------------------+--------------------------+-------------------------------------------+
| ``--password``            | ssh password             | Unlockes RSA key when used with ``-k``    |
+---------------------------+--------------------------+-------------------------------------------+
| ``--key``                 | RSA Key                  | Unlocked via ``-p`` if supplied           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--jump-server``         | ip of jump host          | DNS records may also be used              |
+---------------------------+--------------------------+-------------------------------------------+
| ``--jump-port``           | jump host ssh port       | ``22`` is used unless specified           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--jump-username``       | jump host ssh username   | Username for jump host ssh authentication |
+---------------------------+--------------------------+-------------------------------------------+
| ``--jump-password``       | jump host ssh password   |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--jump-key``            | jump host RSA key        |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--filename``            | output file              |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--repository``          | enable kernel repo       | Default state is disabled                 |
+---------------------------+--------------------------+-------------------------------------------+
| ``--repository-url``      | custom repo url          | Defaults to threat response modules       |
+---------------------------+--------------------------+-------------------------------------------+
| ``--repository-manifest`` | custom repo url          | Defaults to "primary"                     |
+---------------------------+--------------------------+-------------------------------------------+
| ``--gpg-no-verify``       | disable signature checks |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--workers``             | worker count             | Constrains parallel captures              |
+---------------------------+--------------------------+-------------------------------------------+
| ``--verbose``             | log debug messages       |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--log-dir``             | log directory            |                                           |
+---------------------------+--------------------------+-------------------------------------------+
| ``--log-prefix``          | log file prefix          |                                           |
+---------------------------+--------------------------+-------------------------------------------+

Config
------

The ``-c`` and ``--config`` flags accept a relative or absolute path to a yml config file.
The structure of this file is outlided in the ``Configuration`` section below.

Server
------

The ``--server`` flag specifies the server being targeted for memory capture.
A DNS record or IP address are valid inputs.

Version
-------

The ``--version`` flag prints the module version.

Bucket
------

The ``--bucket`` flag specifies the destination bucket when dumping memory to s3.
This flag cannot be used in conjunction wth ``-o`` or ``--output-dir``.

Output-Dir
----------

The ``--output-dir`` flags specify the destination folder when dumping memory to the local filesystem.
This flag  cannot be used in conjunction with ``--bucket``.

Port
----

The ``--port`` flag specifies the port that ssh is running on the remote server specified by ``--server``.
This flag is optional and port ``22`` will be assumed if no value is provided.

Username
--------

The ``--username`` flag specifies the user account to authenticate with when connecting to the remote server specified by ``--server``.

Module
------

The ``--module`` flag accepts a relative or absolute path to a `LiME <https://github.com/504ensicsLabs/LiME>`__ kernel module.
This flag is required if no kernel module repository is enabled with the ``--repository`` flag.

Password
--------

The ``--password`` flag specifies the password used for authentication with connection to the remote server specified by ``--server``.
When used in conjuction with the ``--key`` flag this password will be used to unlock a password protected private key file.

Key
---

The ``--key`` flag accepts a relative or absolute path to a a private key file used for authentication when connecting to the server specified by ``-server``.
If the private key file specified is password protected use the ``-p`` or ``--password`` flags to specify the password that unlocks the private key.

Filename
--------

The ``--filename`` flags specify the name of the file memory will be saved to when dumping to the local filesystem.
The file will be saved to the local directory unless the ``--output-dir`` option is configured.

Repository
----------

The ``--repository`` flag enables automatic kernel module resolution via the repository configured with ``--repository-url``.
Margarita Shotgun will not query any repositories unless explicitly enabled with the ``--repository`` flag.

Repository-Url
--------------

The ``--repository-url`` flag specifies where to search for kernel modules.  The default public repository provided by `Threat Response <http://www.threatresponse.cloud/>`__ is availible at ``https://threatresponse-lime-modules.s3.amazonaws.com``

Repository-manifest
-------------------

The ``--repository-manifest`` flag specifies alternate kernel module manifests in the remote repository configured by ``--repository-url``.  For more information on repository structure and manifests see the :doc:`architecture <architecture>` page or `lime-compiler repository <https://github.com/threatresponse/lime-compiler>`__.

Gpg-no-verify
-------------

The ``--gpg-no-verify`` flag disables gpg verification of kernel modules downloaded from a remote repository.

Workers
-------

The ``--workers`` flag specifies how many worker processes will be spawned to process memory captures in parallel.
The default value for this flag is ``auto`` which will spawn a process per remote host up to the number of cpu cores on the local system.
Integer values can be provided instead of the ``auto`` keyword.
Eg. ``--workers 3`` will process 3 memory captures simultaneously.

Verbose
-------

The ``--verbose`` flag enables debug logging, including each command executed on remote hosts as a part of the memory capture process.

Log-Dir
-------

The ``--log-dir`` flag specifies the directory in which log files will be saved during memory capture.

Log-Prefix
----------

The ``--log-prefix`` flag specifies a custom case number that is prepended onto log files.

Configuration File
******************

Example configuration files are availible in the `repository <https://github.com/ThreatResponse/margaritashotgun/tree/master/conf>`__.
More documentation about the configuration file format is in the works.

Managing AWS Credentials
************************

Margarita Shotgun does not support explicitly declaring aws credentials.  Currently the only way to interact with S3 is by configuring an `aws profile <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html>`__.
A feature is planned to allow selecting a profile other than the ``default`` profile.  Until that feature is completed the ``default`` profile must be used.


Recommended IAM Policy
**************************

Margarita Shotgun only requires PutObject on a specified bucket.

Example
-------

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::member-berries/*"
            }
        ]
    }


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
