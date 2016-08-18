Installation
============

Installation is done by using the ``setup.py`` script.
Since users of these tools are often also developing scripts inside,
this setup script (optionally) does not behave exactly like a typical ``setup.py``.

The current list of valid packages are shown by running with
no arguments::

  $ ./setup.py

You can see the output of this action under `Example Setup`_.

To install another package as a submodule of OpsSpace,
Make sure that the package is in either the CMSCompOps or your
own GitHub account (preferably both).
Add that repository name to ``OpsSpace/config/packagesList.txt``.
Now your repository will be considered a valid package.
Then continue with the setup.

Example Setup
-------------

Below is the output of running the script without any parameters.

.. program-output:: ../setup.py

As you can see, there are valid package names that are the names
of repositories inside the `CMSCompOps GitHub group <https://github.com/CMSCompOps>`_.
Each option is documented in the output above as well.

If I want to freshly install the WorkflowWebTools from dabercro's GitHub on a new machine,
I simply do the following::

  $ ./setup -u dabercro WorkflowWebTools

The origin repository will be set to ``https://github.com/dabercro/WorkflowWebTools.git``
and the remote repository CMSCompOps assumes a centralized version
exists and will be added::

  $ cd WorkflowWebTools && git remote -v
  CMSCompOps      https://github.com/CMSCompOps/WorkflowWebTools.git (fetch)
  CMSCompOps      https://github.com/CMSCompOps/WorkflowWebTools.git (push)
  origin          https://github.com/dabercro/WorkflowWebTools.git (fetch)
  origin          https://github.com/dabercro/WorkflowWebTools.git (push)

.. note::

  Both remote repositories will assume a https connection, so you will need to manually convert the
  remote origin to ssh, if desired.

Members
-------

The setup script can also be imported to gain access to the following members,
but that is an unlikely use case.
However, I will add this so that ``OpsSpace/docs/setup.rst`` can be used as an example
for someone documenting their own scripts or modules.

.. automodule:: setup
   :members:
