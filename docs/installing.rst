
============
Installation
============

System Requirements
*******************

Currently only linux is a supported platform.  Running on OSX or Windows may be possible with minor modifications.

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

Margaritashotgun is not currently listed in PyPi, while we work on that install via one of the methods below.

Installing From Github
**********************

.. code-block:: bash

   $ pip install git+ssh://git@github.com/ThreatResponse/margaritashotgun.git@master
   $ margaritashotgun -h

Local Build and Install
***********************


.. code-block:: bash

   $ git clone https://github.com/ThreatResponse/margaritashotgun.git
   $ cd margaritashotgun
   $ python setup.py
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

