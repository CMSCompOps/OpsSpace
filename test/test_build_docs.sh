#!/bin/bash

# Save here, in case user is not in test dir
here=`pwd`

# Get the test dir
testdir=${0%%`basename $0`}
cd $testdir
testdir=`pwd`

# Get directory or package
opsdir=${testdir%%"/test"}

# Create a virtualenv with your python2.7
virtualenv -p python2.7 venv

# Put virtualenv in your path
PATH=$testdir/venv/bin:$PATH

# Get rid of PYTHONPATH
PYTHONPATH=""

# Install documentation requirements
cd $opsdir
pip install -r docs/requirements.txt

# Install all packages.
# Note that the --force option is used in our
# setup script to install everything.
# That's how readthedocs.org calls setup.py.
./setup.py install --force

# Build the documentation
sphinx-build -b html -E docs test/html
cd $testdir

# Remove the virtualenv
rm -rf venv

cd $here
