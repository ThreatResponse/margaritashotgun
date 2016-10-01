
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

+--------+----------------------+---------------------+----------------------------------------+
| Flag   | Alternate Flag       | Use                 | Notes                                  |
+--------+----------------------+---------------------+----------------------------------------+
| ``-c`` | ``--config``         | path to config file | See the **Configuration File** section |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--server``         | ip of remote server | DNS records may also be used           |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--version``        | print version       |                                        |
+--------+----------------------+---------------------+----------------------------------------+
| ``-b`` | ``--bucket``         | output S3 bucket    | Incommpatible with ``-o``              |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--port``           | ssh port            | ``22`` is used unless specified        |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--username``       | ssh username        | Username for ssh authentication        |
+--------+----------------------+---------------------+----------------------------------------+
| ``-m`` | ``--module``         | lime kernel module  | Required if no repository is enabled   |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--password``       | ssh password        | Unlockes RSA key when used with ``-k`` |
+--------+----------------------+---------------------+----------------------------------------+
| ``-k`` | ``--key``            | RSA Key             | Unlocked via ``-p`` if supplied        |
+--------+----------------------+---------------------+----------------------------------------+
| ``-f`` | ``--filename``       | output file         |                                        |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--repository``     | enable kernel repo  | Default state is disabled              |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--repository-url`` | custom repo url     | Defaults to threat response modules    |
+--------+----------------------+---------------------+----------------------------------------+
| ``-w`` | ``--workers``        | worker count        | Constrains parallel captures           |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--verbose``        | log debug messages  |                                        |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--log-dir``        | log directory       |                                        |
+--------+----------------------+---------------------+----------------------------------------+
|        | ``--log-prefix``     | log file prefix     |                                        |
+--------+----------------------+---------------------+----------------------------------------+

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

The ``-b`` and ``--bucket`` flags specify the destination bucket when dumping memory to s3.

Port
----

The ``--port`` flag specifies the port that ssh is running on the remote server specified by ``--server``.
This flag is optional and port ``22`` will be assumed if no value is provided.

Username
--------

The ``--username`` flag specifies the user account to authenticate with when connecting to the remote server specified by ``--server``.

Module
------

The ``-m`` and ``--module`` flags accept a relative or absolute path to a `LiME <https://github.com/504ensicsLabs/LiME>`__ kernel module.
This flag is required if no kernel module repository is enabled with the ``--repository`` flag.

Password
--------

The ``--password`` flag specifies the password used for authentication with connection to the remote server specified by ``--server``.
When used in conjuction with the ``-k`` or ``--key`` flags this password will be used to unlock a protected private key file.

Key
---

The ``-k`` and ``--key`` flags accept a relative or absolute path to a a private key file used for authentication when connecting to the server specified by ``-server``.
If the private key file specified is password protected use the ``--password`` flag to specify the password that unlocks the private key.

Filename
--------

The ``-f`` and ``--filename`` flags specify the name of the file memory will be saved to when dumping to the local filesystem.

Repository
----------

The ``--repository`` flag enables automatic kernel module resolution via the repository configured with ``--repository-url``.
Margarita Shotgun will not query any repositories unless explicitly enabled with the ``--repository`` flag.

Repository-Url
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

The ``--verbose`` flag enables debug logging, including each command executed on remote hosts as a part of the memory capture process.

Log_Dir
-------

The ``--log-dir`` flag specify the directory in which to log files will be saved during memory capture.

Log_Prefix
----------

The ``--log-prefix`` flag allows a custom case number to be prepended onto log files for easy identification.

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
