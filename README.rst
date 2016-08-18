|build-status| |docs|

Developer Guidelines
====================

When adding functionality to the ToolBox or some new submodule,
please keep track of dependencies that do not come with a fresh
python installation, and ensure that :file:`setup.py`
`installs <setup.html>`_ these dependencies for you.
The easiest way is to have the installer run over a requirements file.

.. note::

  No requirements file exists yet to use OpsSpace.ToolBox,
  but once it is made, make sure to document it here.
  It should be easy to add to setup.py.

If you have requirements for a submodule, :file:`setup.py` will add
these automatically as long as they are listed in :file:`docs/requirements.txt`
inside of this submodule repository.

.. note::

  There's a chance you will have to run setup.py as a sudoer when
  installing packages through pip.

Generating Documentation
------------------------

To test generating documentation for your new tools,
you will need virtualenv installed.
Using the :file:`test/test_build_docs.sh` directory, you can then build the documentation from fresh environment.
This is to mimic the automated documentation building procedure.
From the OpsSpace directory::

  test/test_build_docs.sh

or::

  cd test
  ./test_build_docs.sh

and the OpsSpaceDocs homepage will appear at :file:`test/html/index.html`.

Automated Testing
-----------------

dabercro: |build-status-dabercro|

.. |build-status-dabercro| image:: https://travis-ci.org/dabercro/OpsSpace.svg?branch=master
    :target: https://travis-ci.org/dabercro/OpsSpace
    :alt: Build Status

.. |build-status| image:: https://travis-ci.org/CMSCompOps/OpsSpace.svg?branch=master
    :target: https://travis-ci.org/CMSCompOps/OpsSpace
    :alt: Build Status

.. |docs| image:: https://readthedocs.org/projects/cms-comp-ops-tools/badge/?version=latest
    :target: http://cms-comp-ops-tools.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
