
Architecture
============

Multiprocessing Overview
************************

Coming Soon.


Kernel Module Repository
************************

Kernel Modules can be automatically downloaded from  a remote repository with the ``--repository`` flag.

Repository Structure
--------------------

Legacy repositories were dependent on the xml file listing provided by issuing a ``GET`` request to the root of an amazon s3 bucket.

Metadata files have been introduced to remove s3 hosting as a requirement for repositories.  The official Threat Response repository will continue to be hosted in s3

.. note::

    Kernel modules will continue to be availible at the root of the Threat Response repository until at least the ``0.4.0`` release of Margarita Shotgun.  GPG Signatures will not be provided for these modules.


The new repository structure introduces several new requirements.

1. **Optional** The public portion of the GPG used for signing modules and metadata should present at the root of the repository with the filename ``REPO_SIGNING_KEY.asc``.  If the signing key is not present the ``--gpg-no-verify`` flag must be used with Margarita Shotgun.
2. **Optional** A JSON file with key metadata including the key fingerprint. REPO_SIGNING_KEY.json.
Example:
```
{
"uids": ["Lime Signing Key (Threat Response Official Lime Signing Key) <security@threatresponse.cloud>"],
"fingerprint": "80DA92CB09161F241C8F9BC918BA980367172B17"
}
```
3. **Required** A folder must exist in at the path ``/repodata`` which contains the following files.

   1. **Required** ``repomd.xml`` contains repository metadata including one or more manifests of kernel modules.
   2. **Optional** ``repomd.xml.sig`` detached signature for ``repomd.xml``.  If not present in the repository the ``--gpg-no-verify`` flag must be used with Margarita Shotgun.
   3. **Optional** Manifest files.  Techinally manifests can be stored at any relative path but it is recommended that they be stored in the ``repodata`` directory.

4. **Optional** A ``modules`` directory is recommended which will contain the following files.  Note the following files can have any location relative to the repository root, the ``modules`` directory is simply best practice.

   1. **Required** Compiled lime kernel modules.  Module filenames are arbitrary as the files are explicitly listed in a manifest
   2. **Optional** Detached kernel module signatures.  If signatures are not present the ``--gpg-no-verify`` flag must be used with Margarita Shotgun.  The signature filename is arbitary as it is explicitly listed in a manifest.

Below is an example directory listing of the repository structure.

.. code-block:: text

    ├── REPO_SIGNING_KEY.asc
    ├── REPO_SIGNING_KEY.json
    ├── modules
    │   ├── lime-2.6.32-131.0.15.el6.centos.plus.x86_64.ko
    │   ├── lime-2.6.32-131.0.15.el6.centos.plus.x86_64.ko.sig
    │   ├── ...
    │   ├── lime-4.4.8-20.46.amzn1.x86_64.ko
    │   └── lime-4.4.8-20.46.amzn1.x86_64.ko.sig
    └── repodata
        ├── a134928b6436bae3a9d9d1ddc47cb3c1539d4b559b266c84012ecb2e296b05a5-primary.xml.gz
        ├── repomd.xml.sig
        └── repomd.xml


repomd.xml
----------

The ``repomd.xml`` file contains repository metadata required to resolve kernel modules.

The ``<revision></revision>`` element contains the unix timestamp at which the metadata file was generated.

The structure of a ``<data/>`` element is described in the following table.

+----------------+-----------------------------------------------+
| type           | metadata file type                            |
+----------------+-----------------------------------------------+
| checksum       | checksum of gzipped manifest file             |
+----------------+-----------------------------------------------+
| open_checksum  | checksum of deflated manifest file            |
+----------------+-----------------------------------------------+
| location       | href: path to gzipped manifest file           |
+----------------+-----------------------------------------------+
| timestamp      | last modified timestamp of deflated file      |
+----------------+-----------------------------------------------+
| size           | gzipped filesize                              |
+----------------+-----------------------------------------------+
| open_size      | deflated filesize                             |
+----------------+-----------------------------------------------+


Below is an example repository metadata listing.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <metadata>
      <revision>1474605823</revision>
      <data type="primary">
        <checksum>8d9afbddd9041ed66d3da5db9b1d2d11fbdb5cf6a309d962ac4d1f66fb800551</checksum>
        <open_checksum>a134928b6436bae3a9d9d1ddc47cb3c1539d4b559b266c84012ecb2e296b05a5</open_checksum>
        <location href="repodata/a134928b6436bae3a9d9d1ddc47cb3c1539d4b559b266c84012ecb2e296b05a5-primary.xml.gz"/>
        <timestamp>1474605823</timestamp>
        <size>20726</size>
        <open_size>143916</open_size>
      </data>
    </metadata>


Module manifest
---------------

A manifest consists of multiple module elements inside of a modules element. The module tag and it's child elements are documented in the following table.

+----------------+-----------------------------------------------+
| type           | kernel module type                            |
+----------------+-----------------------------------------------+
| name           | kernel module friendly name                   |
+----------------+-----------------------------------------------+
| arch           | kernel module architecture                    |
+----------------+-----------------------------------------------+
| checksum       | kernel module checksum                        |
+----------------+-----------------------------------------------+
| version        | kernel version targeted by module             |
+----------------+-----------------------------------------------+
| packager       | packager of kernel module                     |
+----------------+-----------------------------------------------+
| location       | href: path to module                          |
+----------------+-----------------------------------------------+
| signature      | href: path to module signature                |
+----------------+-----------------------------------------------+
| platform       | the operating system this module targets      |
+----------------+-----------------------------------------------+

Below is a truncated manifest.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <modules>
      <module type="lime">
        <name>lime-2.6.32-358.11.1.el6.x86_64.ko</name>
        <arch>x86_64</arch>
        <checksum>1d7fc899a95b050a4f434c07012279e84bdd95234420648fbf348f5b4289e9e6</checksum>
        <version>2.6.32-358.11.1.el6.x86_64</version>
        <packager>lime-compiler info@threatresponse.cloud</packager>
        <location href="modules/lime-2.6.32-358.11.1.el6.x86_64.ko"/>
        <signature href="modules/lime-2.6.32-358.11.1.el6.x86_64.ko.sig"/>
        <platform>linux</platform>
      </module>
      ...
      <module type="lime">
        <name>lime-3.10.0-327.28.2.el7.x86_64.ko</name>
        <arch>x86_64</arch>
        <checksum>203e04dbe23ffb0c59d41760e7e8ebc55117e270de6ee17e149107345be6ed0d</checksum>
        <version>3.10.0-327.28.2.el7.x86_64</version>
        <packager>lime-compiler info@threatresponse.cloud</packager>
        <location href="modules/lime-3.10.0-327.28.2.el7.x86_64.ko"/>
        <signature href="modules/lime-3.10.0-327.28.2.el7.x86_64.ko.sig"/>
        <platform>linux</platform>
      </module>
    </modules>


GPG Signatures
--------------

Unless explicitly disabled all kernel modules and metadata files will be checked agains their gpg signature in remote repositories.  Failure to verify a signature, or lack of a signature for a given file is considered a fatal error and will result in a failed memory capture.

.. note::

    Disable signature verification with ``--gpg-no-verify``.
    Checksum verification cannot be disabled.

Build Kernel Modules
--------------------

Kernel modules are build and signed by the `lime-compiler <https://github.com/threatresponse/lime-compiler>`__.  The source is availible and will soon be distributed as a ruby gem for use building private repositories.
