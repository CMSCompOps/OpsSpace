#!/bin/bash

# This test should only be used
# by a package continuous integration test

if [ "$TRAVIS" != "true" ]
then

    echo "This script is designed to be run by travis-ci.org for package tests."
    echo "There should be no need to run it interactively, except for debugging."
    echo "If that is really necessary, do:"
    echo ""
    echo " $ export TRAVIS=\"true\""
    echo ""
    exit 1

else

    env

fi

# Function to do the test for us
_do_test () {


    errors=$1                             # Track how many errors found so far
    packagetest="$2 $3"                   # Setup the test to be done

    $packagetest                          # Do the test
    errorcode=$?                          # Get the error code

    if [ $errorcode -ne 0 ]               # If failed tell user, and increase error count
    then

        tput setaf 1 2> /dev/null
        echo "$packagetest exited with error code $errorcode!"
        errors=$((errors + 1))

    else                                  # If passed, tell for fun too

        tput setaf 2 2> /dev/null
        echo "$packagetest passed!"

    fi

    tput sgr0 2> /dev/null                # Reset colors

    return "$errors"                      # Return total number of errors

}

HOME=$(pwd)                               # Get the package you are testing from location and change HOME
export HOME
package=${HOME##*/}

touch ~/.bashrc                           # Make .bashrc

mkdir OpsSpace/"$package"
# shellcheck disable=SC2046
cp --parents $(git ls-files) OpsSpace/"$package"

cd OpsSpace || exit 1                     # Setup package as a user normally would
# shellcheck disable=SC2154
"$IfSudo" ./setup.py -p "$package"        # Use sudo for the setup if asked with env variable
# shellcheck source=/dev/null
. ~/.bashrc

ERRORSFOUND=0                             # Start tracking errors

# Run all scripts starting with test_
for packagetest in $package/test/test_*
do

    _do_test $ERRORSFOUND "$packagetest"
    ERRORSFOUND=$?

done

# Run main test, with this package required to succeed
_do_test $ERRORSFOUND test/run_tests.sh "$package"
ERRORSFOUND=$?

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
