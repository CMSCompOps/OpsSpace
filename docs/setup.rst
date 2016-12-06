.. _setup-ref:

Installation
============

The installation of Comp Ops tools and scripts can be facilitated by the OpsSpace repository::

    git clone https://github.com/CMSCompOps/OpsSpace.git
    cd OpsSpace

Full installation is done by using the ``setup.py`` script.
Since users of these tools are often also developing scripts inside,
this setup script (optionally) does not compile and install packages like a typical ``setup.py``.
The other method of installation follows these basic steps,
which can also be done by hand, or by running ``setup.py`` with various options described below:

#. The package is downloaded through a given user's repository on GitHub or 
   through the CMSCompOps repository if no user is given.
#. ``setup.py`` searches for ``requirements.txt`` immediately inside any package
   and tries to install the contents through ``pip``.
#. Any script that matches the pattern ``install.??`` inside the package is then run.
#. The script appends the ``OpsSpace`` directory to the user's ``$PYTHONPATH``
   if the appropriate flag is passed.

The current list of valid packages and options are shown by running with no arguments::

  ./setup.py

This gives:

.. program-output:: ../setup.py

To install a non-listed package as a submodule of OpsSpace,
Make sure that the package is in either the CMSCompOps or your
own GitHub account (preferably both).
Add that repository name to the file ``PackageList.txt`` in the OpsSpace root directory.
Now your repository will be considered a valid package.
Then continue with the setup.
Sending a pull request to the ``CMSOpsSpace/OpsSpace`` repository will place your
repository on the Tools & Integration radar, and they will help you to
standardize, document, and test your code.

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

  Both remote repositories will fetch and push over https, so you will need to manually convert
  the remote origin to ssh, if desired.

If the dabercro repository did not exist, then the repository would be cloned from CMSCompOps.
If the ``-u`` option is left blank, then only the CMSCompOps repository is checked.

After downloading desired repositories in this way, you can either install by adding
``<path/to/inside>/OpsSpace`` to your ``$PYTHONPATH``,
or through standard distutils behavior under the ``install`` subcommand.
If you are okay with editing your ``~/.bashrc`` or ``~/.bash_profile``,
then you can automatically add to ``$PYTHONPATH`` by running with the ``-p`` option::

  ./setup.py -p

Or you can run the following, which uses the standard ``distutils`` package::

  ./setup.py install

This first is the recommended method of installation since most users will also be developing
or adjusting their tools as they use them.

.. todo::

  Handle updating (git pull, etc.) inside ``setup.py`` properly.

Troubleshooting
---------------

A list of problems and solutions that come up during ``OpsSpace`` installation and usage should be placed here.

ImportError when using installed pycurl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pycurl`` is needed for the :ref:`dbs-ref` package, which is installed with ``OpsSpace``.
It is possible for ``pycurl`` to be compiled using the wrong ssl backend.
Then when trying to import :py:class:`dbs.apis.dbsClient`, you might get the following error::

    ImportError: pycurl: libcurl link-time ssl backend (nss) is different from compile-time ssl backend (none/other)

To fix this, uninstall ``pycurl`` and reinstall, setting the environment variable ``PYCURL_SSL_LIBRARY`` to match the link-time ssl backend::

    pip uninstall pycurl
    PYCURL_SSL_LIBRARY=nss pip install pycurl

Other systems may use ``openssl`` as the backend.
See `here <http://stackoverflow.com/questions/21096436/ssl-backend-error-when-using-openssl>`_ for more details.

Reference
---------

The setup script can also be imported to gain access to the following members,
but that is an unlikely use case.
However, I will add this so that ``OpsSpace/docs/setup.rst`` can be used as an example
for someone documenting their own scripts or modules.

.. automodule:: setup
   :members:
