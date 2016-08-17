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

For example, the :mod:`WorkflowWebTools` module has the file
:file:`WorkflowWebTools/docs/requirements.txt` that contains

::

    filler

..
  ## .. program-output:: cat ../WorkflowWebTools/docs/requirements.txt

These will be installed automatically, if needed, when calling::

  ./setup.py WorkflowWebTools

.. note::

  There's a chance you will have to run setup.py as a sudoer when
  installing packages through pip.

Generating Documentation
------------------------

To test generating documentation for your new tools,
you will need a few packages installed.
This can be easily done from in the :file:`OpsSpace` directory by::

  ./setup.py --add-doc-tools

or::

  pip install -r docs/requirements.txt

Then you simply have to run::

  make html

and the OpsSpaceDocs homepage will appear at :file:`build/html/index.html`.

