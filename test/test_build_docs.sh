#!/bin/bash

# Save here, in case user is not in test dir
here=`pwd`

# Get the test dir
cd ${0%%`basename $0`}
testdir=`pwd`

if [ "$OPSFULLTEST" != "true" ]
then

    # Create a virtualenv with your python2.7
    # Full test already creates one for you
    virtualenv -p python2.7 venv

    # Put virtualenv in your path
    PATH=$testdir/venv/bin:$PATH

    # Get rid of PYTHONPATH
    PYTHONPATH=""

fi

# Get directory of package
opsdir=${testdir%%"/test"}

# Install documentation requirements
cd $opsdir
pip install -r docs/requirements.txt

# Install all packages.
# Note that the --force option is used in our
# setup script to install everything.
# That's how readthedocs.org calls setup.py.
./setup.py install --force

# Make a directory for output of build log.
outputdir=$testdir/build_out
output=$outputdir/build_out.txt
if [ ! -d $outputdir ]
then

    mkdir $outputdir

fi

# Build the documentation
sphinx-build -b html -E docs test/html > $output
cd $testdir

if [ "$OPSFULLTEST" != "true" ]
then

    # Remove the virtualenv
    rm -rf venv

fi

errorcode=0

if [ "$TRAVIS" = "true" ]
then

    cat $output

fi

if grep "autodoc: failed to import" $output
then

    errorcode=1

fi

cd $here

exit $errorcode
