.. iolite documentation master file, created by
   sphinx-quickstart on Fri Jun 28 16:23:36 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

iolite
==================================
This software package can be used to classify X-ray diffraction datasets of macro-molecular crystallography
with regards to the existence of ice-rings, overlapping spots and mosaicity.


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Installation
------------

To install from source, clone the `GitHub <https://github.com/egrahl/iolite/>`_ repository and then do the following:

.. code-block:: bash

    python setup.py install

Testing
-------

To run the tests, download the source code and do the following:

.. code-block:: bash

    python setup.py test


How to use
==========

iolite can either process multiple datasets of a given directory at once, but its modules can also be run individually on one dataset.

Running multiple datasets at once
---------------------------------
In order to run iolite for multiple datasets, one should create a new directory, in which the processing results of iolite will be saved:

.. code-block:: bash

    mkdir new_directory
    cd new_directory

From this directory one can run iolite_preparation with up to 2 input directories that contain the raw datasets:

.. code-block:: bash

    iolite.iolite_preparation --input1=/path/to/first/input/directory --input2=/path/to/second/input/directory

Ice-rings
---------
In order to classify a dataset whether it has ice-rings or not, the data needs to be imported from the source directory with dials.

.. code-block:: bash

    dials.import *


API documentation
-----------------

Please check out the API documentation :doc:`here <modules/>`.

Issues
------

Please use the `GitHub issue tracker
<https://github.com/egrahl/iolite/issues/>`_ to submit bugs or request
features.

License
-------

Copyright Elin Grahlert, 2019.

.. literalinclude:: ../LICENSE
   :language: text
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


