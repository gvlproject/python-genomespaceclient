Python bindings and commandline client to the GenomeSpace API
=============================================================

.. image:: https://img.shields.io/pypi/v/python-genomespaceclient.svg
   :target: https://pypi.python.org/pypi/python-genomespaceclient/
   :alt: latest version available on PyPI

.. image:: https://coveralls.io/repos/github/gvlproject/python-genomespaceclient/badge.svg?branch=master
   :target: https://coveralls.io/github/gvlproject/python-genomespaceclient?branch=master
   :alt: Code Coverage

.. image:: https://travis-ci.org/gvlproject/python-genomespaceclient.svg?branch=master
   :target: https://travis-ci.org/gvlproject/python-genomespaceclient
   :alt: Travis Build Status

.. image:: https://img.shields.io/pypi/pyversions/python-genomespaceclient.svg
   :target: https://pypi.python.org/pypi/python-genomespaceclient/
   
.. image:: https://readthedocs.org/projects/python-genomespaceclient/badge/?version=latest
   :target: http://python-genomespaceclient.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status
      
This is a python client for the GenomeSpace API. There's a Python API (the
``genomespaceclient`` module), and a command-line script (``genomespace``).


Installation
~~~~~~~~~~~~
Install the latest release from PyPi:

.. code-block:: shell

  pip install python-genomespaceclient


Commandline usage example
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  # Create remote folder, including all intermediate paths
  genomespace -u <username> -p <password> mkdir -p https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/f1/f2/

  # copy local files recursively to remote location
  genomespace -u <username> -p <password> cp -R /tmp/ https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/

  # copy local files matching pattern to remote location - note that paths with wildcards must be enclosed in quotes
  genomespace -u <username> -p <password> cp '/tmp/*.txt' https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/
  
  # list remote files
  genomespace -u <username> -p <password> ls https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/
  
  # move remote file to new location
  genomespace -u <username> -p <password> mv https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/hello.txt https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/world.txt
  
  # download remote files matching pattern, with verbose output
  genomespace -vvv -u <username> -p <password> mv https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/*.txt /tmp/
  
  # delete remote file
  genomespace -u <username> -p <password> rm https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/world.txt


Python usage example
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  from genomespaceclient import GenomeSpaceClient

  client = GenomeSpaceClient(username="<username>", password="<password>")
  client.mkdir("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/f1/f2". create_path=True)
  client.copy("/tmp/", "https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/", recurse=True)
  client.list("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/")
  client.move("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/hello.txt", "https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/world.txt")
  client.copy("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/*.txt", "/tmp/")
  client.delete("https://dm.genomespace.org/datamanager/v1.0/file/Home/MyBucket/*.txt")


Documentation
~~~~~~~~~~~~~
Documentation can be found at https://python-genomespaceclient.readthedocs.org.

