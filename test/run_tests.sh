#!/bin/bash

# Use this environment variable to denote
# which package is being tested in continuous integration
export MUSTWORK=$1

export OPSFULLTEST="true"

if [ "$TRAVIS" != "true" ]
then

    # If not in travis-ci, create a virtualenv
    # to simulate a fresh python installation

    virtualenv -p python2.7 venv          # Create a virtualenv with your python2.7
    export PATH=$testdir/venv/bin:$PATH   # Put virtualenv in your path
    PYTHONPATH=""                         # Get rid of PYTHONPATH

fi

testdir=${0%%/`basename $0`}              # Get the test dir

ERRORSFOUND=0                              # Track errors

for f in $testdir/test_*.??               # Run tests in the testdir
do

    $f                                    # Run test script
    errcode=$?                            # Get error code

    if [ $errcode -ne 0 ]                 # If error, print message
    then

        tput setaf 1 2> /dev/null
        echo "$f exited with error code $errcode!"
        ERRORSFOUND=`expr $ERRORSFOUND + 1`

    else                                  # Otherwise, note success

        tput setaf 2 2> /dev/null
        echo "$f passed!"

    fi

    tput sgr0 2> /dev/null                # Reset color

done

if [ "$TRAVIS" != "true" -a -d venv ]     # Clean up virtualenv, if necessary
then
    rm -rf venv
fi

if [ $ERRORSFOUND -eq 1 ]                 # Setting plural correctly
then                                      #   looks impressive to some
    errstr="error"
else
    errstr="errors"
fi

if [ $ERRORSFOUND -eq 0 ]                 # Set terminal text color depending on result
then
    tput setaf 2 2> /dev/null             # Green: Passed test
else
    tput setaf 1 2> /dev/null             # Red: Did not pass test
fi

echo "$ERRORSFOUND $errstr found"

tput sgr0 2> /dev/null                    # Reset color

exit $ERRORSFOUND                         # Loud exit for travis
