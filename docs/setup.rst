.. _setup-ref:

Installation
============

Installation is done by using the ``setup.py`` script.
Since users of these tools are often also developing scripts inside,
this setup script (optionally) does not behave exactly like a typical ``setup.py``.

The current list of valid packages are shown by running with
no arguments::

  ./setup.py

This gives:

.. program-output:: ../setup.py

To install another package as a submodule of OpsSpace,
Make sure that the package is in either the CMSCompOps or your
own GitHub account (preferably both).
Add that repository name to the file ``PackageList.txt`` in the OpsSpace root directory.
Now your repository will be considered a valid package.
Then continue with the setup.

Example Setup
-------------

If I want to freshly install the WorkflowWebTools from dabercro's GitHub on a new machine,
I simply do the following::

  ./setup -u dabercro WorkflowWebTools

The WorkflowWebTools exists in both the CMSCompOps group and dabercro's fork,
so the setup script will clone from dabercro.
The origin repository will be set to ``https://github.com/dabercro/WorkflowWebTools.git``
and the remote repository CMSCompOps assumes a centralized version
exists and will be added::

  cd WorkflowWebTools && git remote -v

  CMSCompOps  https://github.com/CMSCompOps/WorkflowWebTools.git (fetch)
  CMSCompOps  https://github.com/CMSCompOps/WorkflowWebTools.git (push)
  origin      https://github.com/dabercro/WorkflowWebTools.git (fetch)
  origin      https://github.com/dabercro/WorkflowWebTools.git (push)

.. note::

  Both remote repositories will clone over https, so you will need to manually convert the
  remote origin to ssh, if desired.

If the dabercro repository did not exist, then the repository would be cloned from CMSCompOps.
If the ``-u`` option is left blank, then only the CMSCompOps repository is checked.

After downloading desired repositories in this way, you can either install by adding
``<path/to/inside>/OpsSpace`` to your ``$PYTHONPATH``,
or through standard ``distutils`` behavior under::

  python setup.py install

If you are okay with editing your ``~/.bashrc`` or ``~/.bash_profile``,
then you can automatically add to ``$PYTHONPATH`` by running::

  ./setup.py -d

This is the recommended method of installation since most users will also be developing
or adjusting their tools.

.. todo::

  Handle updating (git pull) inside ``setup.py`` properly.

Members
-------

The setup script can also be imported to gain access to the following members,
but that is an unlikely use case.
However, I will add this so that ``OpsSpace/docs/setup.rst`` can be used as an example
for someone documenting their own scripts or modules.

.. automodule:: setup
   :members:
