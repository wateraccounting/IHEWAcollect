============
Contributing
============

Welcome to the IHE WaterAccounting Collect Tool (IHEWAcollect) project.
Here's how we work.

Code of Conduct
---------------

First of all: the IHEWAcollect project has a code of conduct. Please read the
CODE_OF_CONDUCT.txt file, it's important to all of us.

Rights
------

The GNU General Public License v3.0 license (see LICENSE.rst) applies to
all contributions.

Issue Conventions
-----------------

The IHEWAcollect issue tracker is for actionable issues.

Questions about installation, distribution, and usage should be taken to
the project's `wateraccounting.slack.com#issue
<https://app.slack.com/client/TQP20VD3N/CQTCUH1FA>`__.
Opened issues which fall into one of these three categories may be
perfunctorily closed.

Questions about development of IHEWAcollect, brainstorming, requests for comment,
and not-yet-actionable proposals are welcome in the project's
`wateraccounting.slack.com#idea
<https://app.slack.com/client/TQP20VD3N/CQG1S6909>`__.

IHEWAcollect is a relatively new project and highly active. We have bugs, both
known and unknown.

Please search existing issues, open and closed, before creating a new one.

IHEWAcollect employs Geospatial modules, so bug reports very often hinge on the
following details:

- Operating system type and version (Windows? Ubuntu 12.04? 14.04?)
- The version and source of GDAL (UbuntuGIS? Homebrew?)

Dataset Objects
---------------

Our term for the kind of object that allows read and write access to raster data
is *dataset object*. A dataset object might be an instance of `DatasetReader`
or `DatasetWriter`. The canonical way to create a dataset object is by using the
`IHEWAcollect.GIS.OpenAsArray()` function.

This is analogous to Python's use of
`file object <https://docs.python.org/3/glossary.html#term-file-object>`__.

Git Conventions
---------------

We use a variant of centralized workflow described in the `Git Book
<https://git-scm.com/book/en/v2/Distributed-Git-Distributed-Workflows>`__.  We
have no 1.0 release for IHEWAcollect yet and we are tagging and releasing from the
master branch. Our post-1.0 workflow is to be decided.

Work on features in a new branch of the mapbox/IHEWAcollect repo or in a branch on
a fork. Create a `GitHub pull request
<https://help.github.com/articles/using-pull-requests/>`__ when the changes are
ready for review.  We recommend creating a pull request as early as possible
to give other developers a heads up and to provide an opportunity for valuable
early feedback.

Code Conventions
----------------

IHEWAcollect supports Python 2 and Python 3 in the same code base, which is
aided by an internal compatibility module named ``compat.py``. It functions
similarly to the more widely known `six <https://six.readthedocs.io/>`__ but
we only use a small portion of the features so it eliminates a dependency.

We strongly prefer code adhering to `PEP8
<https://www.python.org/dev/peps/pep-0008/>`__.

Tests are mandatory for new features. We use `pytest <https://pytest.org>`__.

We aspire to 100% coverage for Python modules `Coveralls
<https://coveralls.io/github/wateraccounting/ihewacollect>`__.

Development Environment
-----------------------

Developing IHEWAcollect requires Python 2.7 or any final release after and
including 3.4.  We prefer developing with the most recent version of Python
but recognize this is not possible for all contributors.
See the Windows install instructions in the `readme
<README.rst>`__ for more information about building on Windows.

Initial Setup
^^^^^^^^^^^^^

First, clone IHEWAcollect's ``git`` repo:

.. code-block:: console

    $ git clone https://github.com/wateraccounting/ihewacollect.git

Development should occur within a `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__ to better isolate
development work from custom environments.

In some cases installing a library with an accompanying executable inside a
virtual environment causes the shell to initially look outside the environment
for the executable.  If this occurs try deactivating and reactivating the
environment.

Installing GDAL
^^^^^^^^^^^^^^^

The GDAL library and its headers are required to build IHEWAcollect. We do not
have currently have guidance for any platforms other than Linux and OS X.

On Linux, GDAL and its headers should be available through your distro's
package manager. For Ubuntu the commands are:

.. code-block:: console

    $ sudo add-apt-repository ppa:ubuntugis/ppa
    $ sudo apt-get update
    $ sudo apt-get install gdal-bin libgdal-dev

On OS X, Homebrew is a reliable way to get GDAL.

.. code-block:: console

    $ brew install gdal

Python build requirements
^^^^^^^^^^^^^^^^^^^^^^^^^

Provision a virtualenv with IHEWAcollect's build requirements.  IHEWAcollect's
``setup.py`` script will not run unless Cython and Numpy are installed, so do
this first from the IHEWAcollect repo directory.

Linux users may need to install some additional Numpy dependencies:

.. code-block:: console

    $ sudo apt-get install libatlas-dev libatlas-base-dev gfortran

then:

.. code-block:: console

    $ pip install -U pip
    $ pip install -r requirements-dev.txt

Installing IHEWAcollect
^^^^^^^^^^^^^^^^^^^^^^^

Installing IHEWAcollect in editable mode while
developing is very convenient but only affects the Python files.

.. code-block:: console

    $ python setup.py install

Uninstalling IHEWAcollect
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pip uninstall IHEWAcollect

Running the tests
^^^^^^^^^^^^^^^^^

IHEWAcollect's tests live in ``python setup.py test`` and generally match the main
package layout.

To run the entire suite and the code coverage report:

.. code-block:: console

    $ python setup.py test
