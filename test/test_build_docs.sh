#!/bin/bash

# Save here, in case user is not in test dir
here=$(pwd)

# Get the test dir
cd "${0%%$(basename "$0")}" || exit 1
testdir=$(pwd)

if [ "$OPSFULLTEST" != "true" ]
then

    # Create a virtualenv with your python2.7
    # Full test already creates one for you
    virtualenv -p python2.7 venv

    # Put virtualenv in your path
    PATH=$testdir/venv/bin:$PATH

    # Get rid of PYTHONPATH
    PYTHONPATH=""
    echo "PYTHONPATH: $PYTHONPATH"

fi

# Get directory of package
opsdir=${testdir%%"/test"}

# Install documentation requirements
cd "$opsdir" || exit 1
pip install -r docs/requirements.txt

# Install all packages.
# Note that the --force option is used in our
# setup script to install everything.
# That's how readthedocs.org calls setup.py.
./setup.py install --force

# Make a directory for output of build log.
outputdir="$testdir/build_out"
output="$outputdir/build_out.txt"

test -d "$outputdir" || mkdir "$outputdir"


# Build the documentation and redirect errors for analysis
sphinx-build -b html -E docs test/html 2> "$output"
cd "$testdir" || exit 1

if [ "$OPSFULLTEST" != "true" ]
then

    # Remove the virtualenv
    rm -rf venv

fi

errorcode=0

if [ "$TRAVIS" = "true" ]
then

    cat "$output"

fi

if grep "autodoc: failed to import" "$output"
then

    tput setaf 1 2> /dev/null
    echo "Import failed in documentation build!"

    if  [ "$CHECKDOC" = "true" ]
    then

        errorcode=1

    else

        tput setaf 1 2> /dev/null
        echo "Will only result in failed test if CHECKDOC=true is set."

    fi

fi

tput sgr0 2> /dev/null

cd "$here" || exit 1

exit "$errorcode"
