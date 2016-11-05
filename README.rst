|build-status| |docs|

.. |build-status| image:: https://travis-ci.org/CMSCompOps/OpsSpace.svg?branch=master
    :target: https://travis-ci.org/CMSCompOps/OpsSpace
    :alt: Build Status

.. |docs| image:: https://readthedocs.org/projects/cms-comp-ops-tools/badge/?version=latest
    :target: http://cms-comp-ops-tools.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. _developer-ref:

Developer Guidelines
====================

One of the main goals of this project is to gather scripts to be used by future members of CMS.
This means that the scripts must be easy to use and easy to maintain.
We have set up a system that tests any code in a pull request,
as well as automatically documents any approved pull request.
Trying to adhere to the following guidelines will allow for these processes to go smoothly.
The Tools & Integration team recognizes that we will likely gather lots of useful code
that does not follow these standards, but be aware that one of our goals is to clean scripts.
If you hope to contribute complex code, please write good tests to ensure it doesn't break.

.. contents:: :local:

Security
--------

Since we are hosting our code on GitHub, anyone can look at our code.
We have decided to keep the code on GitHub to avoid
a false sense of security offered by private provided by private repositories.
GitHub is also supported by a range of useful third-party applications.
(There will be more on that in :ref:`gen-docs-ref` and 
:ref:`tests-ref`.)

Since we are using this open source model, care should be taken that usernames and
passwords are not placed in the repository.
Also, when developing code for services running on certain machines,
the specific machine hostname or IP address should not be given.

.. _style-ref:

Style Guidelines
----------------

.. note::

  If you are an expert in some used language, feel free to recommend a guide and impliment tests.

Python Style
~~~~~~~~~~~~

In order to make the code more readable for future users, we encourage everyone to try to follow
the `PEP 8 Style Guide <https://www.python.org/dev/peps/pep-0008/>`_ for any code written in Python.
We anticipate that most of the APIs and scripts added will be in Python.
As the project grows and gains more languages, we will recommend style guides for other languages.

To help check if your python code follows PEP 8 conventions, we have implimented a test.
The test depends on the `pylint <https://pylint.readthedocs.io/en/latest/>`_ package.
If you have ``pip`` installed, ``pylint`` can easily be added with::

  pip install pylint

The style can be tested with the ``test/test_style.py`` script, relative to the ``OpsSpace`` directory.

In addition to checking for PEP 8 conventions,
the docstrings of every module, function, and method will be checked for adequate documentation.
This means each parameter and a function's return must be documented.
For each module, we ask that you at least start with a docstring containing the name of the author.
This will help the Tools & Integration team as well as users know who to contact if questions arise.
Our documentation system, sphinx, will then automatically create reference pages.
For example, if you document ``example.py`` the following way:

.. program-output:: cat example.py

Sphinx can show your module to users as the following:

.. automodule:: example
   :members:
   :noindex:

You can read more about the
`autodocumentation features <http://www.sphinx-doc.org/en/stable/ext/autodoc.html>`_
of Sphinx here.
There will also be more details under :ref:`gen-docs-ref`.

Last but not least, there is also a test for code complexity.
These tests ensure that there are not too many variables floating around in a fuction or method.
Also, if excessive branching is truly necessary, this will require the developer to create
additional methods that will also need to be documented.
This may clash with many people's existing coding styles,
but the Tools & Integration Team has already seen that refactoring code to pass these tests
results in code that is significantly easier to follow and better documented.

.. note::

  If you run tests over ``setup.py`` inside of a virtual environment,
  pylint will not import distutils, resulting in a failed test.
  If you changed ``setup.py``, please run::

    test/test_style.sh

  separately to ensure good documentation practice.

If you have a good reason that your code does not pass the style test,
you can disable a certain kind of check for a file.
For example, the :ref:`workflow-info-ref` module makes an HTTPS connection,
and CMS certificates are not considered valid.
Python 2.6 doesn't make this check, but in Python 2.7,
there is a workaround that includes a new keyword and accessing a private member of the ssl module.
The log file of the check will include warnings that end with ``(protected-access)`` and
``(unexpected-keyword-arg)`` (for Python 2.6 tests).
To tell ``pylint`` to ignore these shortcomings and
to warn future developers of what might pop up in the code,
place a line like the following at the top of the script or module::

    # pylint: disable=protected-access, unexpected-keyword-arg

See this
`Pylint FAQ <https://pylint.readthedocs.io/en/1.6.0/faq.html#is-there-a-way-to-disable-a-message-for-a-particular-module-only>`_
for more details.

JavaScript Comments
~~~~~~~~~~~~~~~~~~~

Comments can be pull from JavaScript if you start a comment block with ``/*"""`` and end with ``/*``.
The indentation of the comments must line up with the first ``/`` starting the comment block,
or Sphinx will refuse to render the content.

For example, you would write JavaScript comment blocks in the following way.

.. program-output:: cat example.js

See :ref:`js-docs-ref` to see how those comments are rendered.

.. _shell-style-ref:

Shell Style
~~~~~~~~~~~

The third-party tool ShellCheck (https://github.com/koalaman/shellcheck) has been chosen as the standard to hold ``.sh`` scripts to.
The repository's README describes how to install and run ShellCheck.
When running, the tool will give an error number and short description for each line that is potentially problematic.
For example, if I have a line like the following in a shell script::

    shellcheck $(git ls-files | grep "\.sh")

I will get a message from ShellCheck when running on that script like the following::

    shellcheck $(git ls-files | grep "\.sh")
               ^-- SC2046: Quote this to prevent word splitting.

Details of each error can be found in the repository's Wiki.
For example, the error ``SC2046`` is described at https://github.com/koalaman/shellcheck/wiki/SC2046.
In the example above, I actually want word splitting, so to disable the message for this line, the ``.sh`` file would be edited to contain::

    # shellcheck disable=SC2046
    shellcheck $(git ls-files | grep "\.sh")

Comment Blocks
++++++++++++++

Sphinx has also been configured to handle shell script block comments.
For these comment blocks to show up automatically in the documentation,
they must begin and end with a lone line of ``##!``.
Each line in the block must be preceded then by a ``#`` and a space (or be a lone ``#``).
Any additional indentation past the first space will be preserved by the analyzer.

For example, you would want a block comment to look like the comment in the following script.

.. program-output:: cat example.sh

See :ref:`shell-docs-ref` to see how that comment block is rendered.

Ensuring an Easy Installation
------------------------------

One reason why some people may rewrite tools is that it is difficult to get some older
scripts to work the way as advertised.
We want to make the installation process as painless as possible for the user.
By following the following guidelines, it should be easy for the Tools & Integration
team to continuously test installation procedures.

CMSToolBox
~~~~~~~~~~

When adding functionality to the ToolBox or some new submodule,
please keep track of dependencies that do not come with a fresh
python installation, and ensure that ``setup.py``
:ref:`installs <setup-ref>` these dependencies for you.
The easiest way is to have the installer run over a requirements file.

.. note::

  No requirements file exists yet to use OpsSpace.CMSToolBox,
  but once it is made, make sure to document it here.
  It should be easy to add to ``setup.py``,
  which already handles requirements files to generate
  documentation and to install other CMSCompOps packages.

.. _install-module-ref:

Additional Module Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install another repository inside of OpsSpace as an additional module to CMSToolBox,
simply have a copy of the repository under the `CMSCompOps GitHub group <https://github.com/CMSCompOps>`_,
and add the name of the repository to ``PackageList.txt``.
If you have requirements for a submodule, ``setup.py`` will add these automatically through ``pip``
as long as they are listed in ``requirements.txt`` inside the root of the submodule repository.

.. note::

  There's a chance you will have to run setup.py as a sudoer when
  installing packages through pip.

.. todo::

  Properly propagate and test the ``--user`` installation option through ``setup.py``.

If your repository require special CMS tools that are not installable through ``pip``,
the ``setup.py`` script also looks for any ``install.??`` file in the root directory
of the repository and runs the first one it finds.
This happens after attempting to install the contents of the ``requirements.txt``.
Make sure that your ``install.??`` file is executable::

    chmod +x install.??

There are details about how to use the install script on the
:ref:`installation page <setup-ref>`, but the steps that the script takes are outlined here:

#. The repository is downloaded from CMSCompOps repository, or from the specified user's GitHub repository.
#. ``pip.main()`` is run over the repository's ``requirements.txt`` file, if it exists.
#. One ``install.??`` file is run through ``os.system('<repo>/install.??')``, if it exists.

Make sure that these steps do everything needed to pass a package's :ref:`tests <tests-ref>`.

.. _gen-docs-ref:

Generating Documentation
------------------------

The easiest way to generate documentation is through our test script.
To use the test script to generate documentation for your new tools, you will need virtualenv installed::

    pip install virtualenv

Using the ``test/test_build_docs.sh`` directory, you can then build the documentation from fresh environment.
From the OpsSpace directory, you can run::

  test/test_build_docs.sh

or::

  cd test
  ./test_build_docs.sh

and the OpsSpaceDocs homepage will appear at ``test/html/index.html``.

The use of a virtual environment is to mimic the automated documentation building procedure on
`readthedocs <https://docs.readthedocs.io/en/latest/index.html>`_.
It prevents dependencies unknown to OpsSpace from causing the documentation generation to fail.
If you do not want to reinstall python through a virtual environment every time, just to check minor changes,
install sphinx and the used extensions.
This can be done by running over the following requirements file::

    pip install -r docs/requirements.txt

Then from the OpsSpace root, run::

    sphinx-build -b html -E docs test/html

This will build the documentation the same way as ``test_build_docs.sh``.
Feel free to change options to build other formats or cache generated files.

Adding Webpages
~~~~~~~~~~~~~~~

The documentation webpages are generated by ``.rst`` files within the ``OpsSpace/docs`` directory.
To add a new page to our documentation, create a new ``.rst`` file (or softlink to an ``.rst`` file),
and list the file as Contents inside of ``index.rst``.

This will need to be done most often when adding a new package, which will have its own page.
The recommended method for adding additional documentation for a package is
to softlink to where the ``<package>/README.rst`` file would be if the package was installed,
relative to the ``docs`` directory of ``OpsSpace``.
If using the ``test/test_build_docs.sh`` file to generate documentation, all of the modules
in ``PackageList.txt`` will be downloaded from the CMSCompOps GitHub,
so the page will be where it belongs if the instructions under :ref:`install-module-ref` are followed.
Linking to the ``README.rst`` will allow viewers on GitHub can also see your ``README.rst`` on the package homepage.
Just remember, the autodoc feature of Sphinx does not work on GitHub.
If all of your ``README.rst`` is autodoc, then it will be blank on GitHub.

.. _example-ref:

Python Documentation
~~~~~~~~~~~~~~~~~~~~

If adding a module to ``CMSToolBox``, edit the ``toolbox.rst`` to autodocument your modules.
Examples of this are contained in ``toolbox.rst``,
but let's quickly return to the examples under :ref:`style-ref`.
The ``example.py`` module, that is written this way:

.. program-output:: cat example.py

can be automatically documented in these ``.rst`` pages by typing::

    .. automodule:: example
       :members:

giving:

.. automodule:: example
   :members:

The full name of the module used in the import statement must be used to generate the documentation.
If adding a submodule inside of the CMSToolBox module, replace the ``example`` above with
``CMSToolBox.<module_name>``.
The configuration has ``OpsSpace`` in its path by default.
If you need to add a path for importing isolated python scripts,
create a file called ``test/path.txt`` inside your repository.
:ref:`You should have a test directory <tests-ref>`,
so this location is chosen to keep the repository structure relatively clean.
This file should include folder names relative to the repository root that will be added to
Sphinx's system path.

For example, the example.py script under :ref:`example-ref` are in the ``OpsSpace/docs`` folder.
The ``OpsSpace/test/path.txt`` file contents are just:

.. program-output:: cat ../test/path.txt

Sphinx is set up to update its path automatically to import this.

.. Note::

  The path is just for importing python scripts.
  All other scripts must use one of the custom documenters,
  which require paths relative to ``OpsSpace/docs``.

.. _js-docs-ref:

JavaScript Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

To document JavaScript written this way:

.. program-output:: cat example.js

you would add the following to your ``.rst`` pages::

    .. autoanysrc:: phony
       :src: example.js
       :analyzer: js

The ``:src:`` must be the full path relative to the ``docs`` directory.
This will be inserted into your documentation as follows:

.. autoanysrc:: phony
   :src: example.js
   :analyzer: js

.. _shell-docs-ref:

Shell Script Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

To document shell scripts written this way:

.. program-output:: cat example.sh

you would add the following to your ``.rst`` pages::

    .. autoanysrc:: phony
       :src: example.sh
       :analyzer: shell-script

Again, the ``:src:`` must be the full path relative to the ``docs`` directory.
This will be inserted into your documentation as follows:

.. autoanysrc:: phony
   :src: example.sh
   :analyzer: shell-script

.. _tests-ref:

Writing Automated Tests
-----------------------

To maintain stability in your contributed tools, tests should be written.
That will prevent future contributors from committing a change that breaks functionality.
Tools & Intergration has set up automatic tests through
`Travis Continuous Integration <https://travis-ci.org/>`_,
a third-party tool available to GitHub users.

Any executable script added to the ``test`` directory of OpsSpace or your package
that matches the pattern ``test/test_*`` will be run as part of this automated test.
Any non-zero exit code of this script will cause Travis CI to report the build as failed.
The test is triggered by each push, pull request, and merge.

The style guide for the tests is not so strict.
Good tests should be written and forgotten.
In the event of a failure though, it should be possible for
someone else to figure out what went wrong from the log files.

The CMSCompOps group's OpsSpace is already set up to run these tests automatically.
To run tests in another package, a file called ``.travis.yml`` should be created in the repository's root directory.
The most basic example of this file would have the following contents::

    language: python
    python: 2.7
    install: git clone https://github.com/CMSCompOps/OpsSpace.git
    script: OpsSpace/test/package_test.sh

CMS Comp Ops has agreed to support Python 2.7, but you can also run tests using Python 2.6 by replacing
the version line with::

    python:
      - 2.6
      - 2.7

The default test is run on Ubuntu 12.04.
There are some python newer packages that cannot be installed through ``pip`` on this old release.
To run the test on Ubuntu 14.04 (which is considered stable for now), add the following lines to ``.travis.yml``::

    sudo: required
    dist: trusty

To confirm that your package is being documented correctly (i.e. Sphinx can import everything correctly), you should have the settings::

    dist: trusty
    sudo: required
    python: 2.7
    env: CHECKDOC=true

Even if you don't run the documentation check, any failed documentation builds will break
all other repository's tests, so someone will probably offer to help you fix it.

If you have shell scripts in your repository, you should also install shellcheck during the build test.
See :ref:`shell-style-ref` for more details.
Place the following lines anywhere in your ``.travis.yml`` file to do that::

    addons:
      apt:
        sources: debian-sid
        packages: shellcheck

Then activate your repository as briefly described in the :ref:`fork-status-ref` below.

For more information on the configuration, see the `Travis CI documentation <https://docs.travis-ci.com/>`_.
We ask that you do not change the ``install`` or ``script`` steps though.
These will install your package through the ``setup.py`` method for `Ensuring an Easy Installation`_.
The ``package_test.sh`` file will run all tests matching the pattern ``test/test_*`` inside your repository.

.. _fork-status-ref:

OpsSpace Forks' Build Statuses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is easy to run the OpsSpace build tests on your own forks.
The only thing used to configure the tests is the ``.travis.yml`` file that is already in OpsSpace.
After that, connect your GitHub account at `Travis CI <https://travis-ci.org/>`_ and activate your fork.
Feel free to link to your status badge below so that you can easily see your own build status
on the rendering of the GitHub README.
This way, you can check the automatic build results before making a pull request.

dabercro: |build-status-dabercro|

.. |build-status-dabercro| image:: https://travis-ci.org/dabercro/OpsSpace.svg?branch=master
    :target: https://travis-ci.org/dabercro/OpsSpace
    :alt: Build Status
