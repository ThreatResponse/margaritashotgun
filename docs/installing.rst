
============
Installation
============

System Requirements
*******************

Margarita Shotgun is supported on common linux distributions, for other operating systems see the `Install with Docker <https://margaritashotgun.readthedocs.io/en/latest/installing.html#install-with-docker>`__ section.

While margaritashotgun is written purely in python, some of the libraries used require additional system packages.

Fedora / RHEL Distributions
---------------------------

* python-devel (2.X or 3.X)
* python-pip
* libffi-devel
* openssl-devel

Debian Distributions
--------------------

* python-dev (2.X or 3.X)
* python-pip
* libffi-dev
* libssl-dev

Install From PyPi
*****************

.. code-block:: bash

   $ pip install margaritashotgun


Install with Docker
*******************

Pull and run the `python docker image <https://hub.docker.com/_/python/>`__.

.. code-block:: bash

   $ docker pull python:3
   $ docker run -ti python:3 bash
   $ root@3009a5bc9817:/# pip install margaritashotgun

.. note::

   If you plan on streaming memory to S3 ensure you setup IAM access keys in the docker container.
   Set ``-e ACCESS_KEY_ID=ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=ACCESS_KEY`` in the ``docker run`` command above.
   Alternately follow `Amazon's guide <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html>`__ for configuring credentials once the docker container is running.


Install From Github
*******************

.. code-block:: bash

   $ pip install git+ssh://git@github.com/ThreatResponse/margaritashotgun.git@master
   $ margaritashotgun -h

Local Build and Install
***********************


.. code-block:: bash

   $ git clone https://github.com/ThreatResponse/margaritashotgun.git
   $ cd margaritashotgun
   $ python setup.py sdist
   $ pip install dist/margarita_shotgun-*.tar.gz
   $ margaritashotgun -h

Local Execution
***************

In the previous two example dependencies are automatically resolved, if you simply want to run margaritashotgun using the script ``bin/margaritashotgun`` you will have to manually install dependencies

.. code-block:: bash

   $ git clone https://github.com/ThreatResponse/margaritashotgun.git
   $ cd margaritashotgun
   $ pip install -r requirements.txt
   $ ./bin/margaritashotgun -h

