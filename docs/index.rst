.. iolite documentation master file, created by
   sphinx-quickstart on Fri Jun 28 16:23:36 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

iolite
==================================
This python package can be used to classify X-ray diffraction datasets of macro-molecular crystallography
with regards to the existence of ice-rings, overlapping spots and mosaicity.


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Installation
------------

To install from source, clone the `GitHub <https://github.com/egrahl/iolite/>`_ repository and then do the following:

.. code-block:: bash

    python setup.py install

To use *iolite* for developing, run the following in the directory containing the setup.py:

.. code-block:: bash

    python setup.py develop --user
    export PATH=$PATH:~/.local/bin

Testing
-------

To run the tests, download the source code and do the following:

.. code-block:: bash

    python setup.py test

How to use
----------

A tutorial explaining how to use *iolite* can be found under */docs/iolite_tutorial.rst* . 



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


