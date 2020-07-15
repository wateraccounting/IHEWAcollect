===========
Development
===========

Download source code from `Github <https://github.com/wateraccounting/IHEWAcollect>`_.

.. code-block:: console

    $ git clone https://github.com/wateraccounting/IHEWAcollect.git
    $ cd IHEWAcollect

In the PyCharm IDE, change "Project Structure -> Source Folders" to "src"

From the root of the project

.. code-block:: console

    $ python setup.py --version

Format scripts by PEP8

.. code-block:: console

    $ autopep8 --in-place --aggressive src/IHEWAcollect/base/base.py

Flake8, pre-commit

.. code-block:: console

    $ pre-commit install

    $ pre-commit run --all-files
    [INFO] Initializing environment for git://github.com/pre-commit/pre-commit-hooks.
    [INFO] Initializing environment for https://github.com/pre-commit/mirrors-isort.
    [INFO] Installing environment for git://github.com/pre-commit/pre-commit-hooks.
    [INFO] Once installed this environment will be reused.
    [INFO] This may take a few minutes...
    [INFO] Installing environment for https://github.com/pre-commit/mirrors-isort.
    [INFO] Once installed this environment will be reused.
    [INFO] This may take a few minutes...

Unit test

.. code-block:: console

    $ python setup.py test

Read the Docs

.. code-block:: console

    $ python setup.py doctest

    $ python setup.py docs

Upload to PyPI

1. In IDE, **commit** the changes "**v0.0.1**"
2. In IDE, **Version Control -> Log**, select this commit
3. In IDE, add version tag, select **VCS -> Git -> tag**
4. In IDE, **Tag window -> Tag Name**, type "**v0.0.1**"

5. In cmd, build package, type ``python setup.py sdist bdist_wheel``
6. In cmd, validate build, type ``twine check dist/IHEWAcollect-0.0.1*``
7. In cmd, upload build, type ``twine upload dist/IHEWAcollect-0.0.1*``

8. In IDE, **push** the commit, with Tag label: "*HEAD*", "*master*", "*v0.0.1*"
9. In Github, select **Release** to "create a new release" or "Draft a new release"
10. In Github, **Tag version**, type "**v0.0.1**"
11. In Github, **@ Target**, select this commit
12. In Github, **Publish release**
