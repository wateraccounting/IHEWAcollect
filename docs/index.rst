============
IHEWAcollect
============

This is the documentation of **IHEWAcollect**.

.. code-block:: console

    $ git clone https://github.com/wateraccounting/IHEWAcollect.git

From the root of the project

.. code-block:: console

    $ python setup.py --version

Format scripts by PEP8

.. code-block:: console

    $ autopep8 --in-place --aggressive src/IHEWAcollect/base/base.py

Unit test

.. code-block:: console

    $ python setup.py test

Read the Docs

.. code-block:: console

    $ python setup.py doctest

    $ python setup.py docs

PyPI upload, run ``setup.py``::

    1. Commit -> Git - tag - add - v0.0.1 -> ``setup.py`` -> push
    2. Github - Release - new release v0.0.1

.. code-block:: console

    $ python setup.py sdist bdist_wheel

    $ twine check dist/*

    $ twine upload dist/*

.. warning::

    Must contain **config.yml** and **accounts.yml-encrypted** file.


Contents
========

.. toctree::
   :maxdepth: 4

   License <license>
   Authors <authors>
   Contributing <contributing>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Google style: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
