Margarita Shotgun
=================

Python Remote Memory Aquisition

Documentation
-------------

Read the full documentation on `read the docs <https://margaritashotgun.readthedocs.io/en/latest/>`__.

Quickstart
**********

For more information see the `user guide <https://margaritashotgun.readthedocs.io/en/latest/user_guide.html/>`__.

Installation
~~~~~~~~~~~~

``pip install git+ssh://git@github.com/ThreatResponse/margaritashotgun.git@master``

Or see `installing <https://margaritashotgun.readthedocs.io/en/latest/installing.html>`__.

Capture A Single Machine
************************

A single machine can be captured using only the command line arguments for margaritashotgun.
First specify the server and user with the ``-s`` and ``-u`` flags respectively.
Next provide a path to an ssh key with ``-k`` (or use a password with the ``-p`` flag).
Finally provide a lime kernel module with ``-m`` and specify an output file with ``-f``

::

   margaritashotgun -s 172.16.20.10 -u root -k root_access.pem -m lime-3.13.0-74-generic.ko -f 172.16.20.10-mem.lime

Save Memory In S3
*****************

To save a file to s3 simply replace the ``-f`` or ``filename`` flags with ``-b`` or ``--bucket``.  Ensure that you have aws credentials configured prior to executing the following command.

::

   margaritashotgun -s 172.16.20.10 -u root -k root_access.pem -m lime-3.13.0-74-generic.ko -b memory_capture_bucket``

Capture Multiple Machines
*************************

Run margaritashotgun with a configuration file like ``parallel_config.yml.example``

.. code-block:: bah

    aws:
        bucket: memory_dump_example
    hosts:
        - addr:     52.36.191.XXX
          port:     22
          username: ec2-user
          key:      access.pem
          module:   lime-4.1.19-24.31.amzn1.x86_64.ko
        - addr:     52.36.170.XXX
          port:     22
          username: ec2-user
          key:      access.pem
          module:   lime-4.1.19-24.31.amzn1.x86_64.ko
        - addr:     52.36.210.XXX
          port:     22
          username: ubuntu
          key:      dev.pem
          module:   lime-3.13.0-74-generic.ko
        - addr:     52.36.90.XXX
          port:     22
          username: ubuntu
          key:      dev.pem
          module:   lime-3.13.0-74-generic.ko
    workers: 2

Here parallelism is limited to 2 workers.

Run the capture with:

::

   margaritashotgun -c your_custom_config.yml.

License
-------

The MIT License (MIT)

Copyright (c) 2016 Joel Ferrier

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
