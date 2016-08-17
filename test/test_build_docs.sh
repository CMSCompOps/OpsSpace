#!/bin/bash

# Save here, in case user is not in test dir
here=`pwd`

# Get the test dir
testdir=${0%%`basename $0`}
cd $testdir
testdir=`pwd`

# Create a virtualenv with your python2 interpreter
virtualenv -p python2 venv

# Put virtualenv in your path
PATH=$testdir/venv/bin:$PATH

# Install documentation requirements
cd ..
pip install -r docs/requirements.txt

# Install all packages.
# Note that the --force option is used in our
# setup script to install everything.
# That's how readthedocs.org calls setup.py.
./setup.py install --force

# Print out some pylint scores.
# Need to clean this up in the future.
pylint --rcfile docs/pylint.cfg setup.py
pylint --rcfile docs/pylint.cfg CMSToolBox

for d in `cat config/packagesList.txt`
do
    pylint --rcfile docs/pylint.cfg $d
done

# Build the documentation
sphinx-build -b html -E docs test/html
cd $testdir

# Remove the virtualenv
rm -rf venv

cd $here
