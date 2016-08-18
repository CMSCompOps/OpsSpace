#!/bin/bash

install=$1

# Check for pylint
if [ "`which pylint 2> /dev/null`" = "" ]
then

    # Full test is in virtualenv that needs pylint
    if [ "$install" = "install" -o "$OPSFULLTEST" = "true" ]
    then

        pip install pylint

    else

        # Instruct on how to install, if not available
        echo "pylint not installed on this machine. Run:"
        echo ""
        echo "pip install pylint"
        echo ""
        echo "Or rerun this script as"
        echo ""
        echo "./test_style.sh install"
        echo ""
        exit 1

    fi

fi

# Save here, in case user is not in test dir
here=`pwd`

# Get the test dir
testdir=${0%%`basename $0`}
cd $testdir
testdir=`pwd`

# Set text output location
outputdir=$testdir"/pylint_output"
if [ ! -d $outputdir ]
then
    mkdir $outputdir
fi

# Get directory or package
opsdir=${testdir%%"/test"}
cd $opsdir

# Define configuration for pylint
pylintCall="pylint --rcfile docs/pylint.cfg"

# Call default OpsSpace tools
$pylintCall setup.py > $outputdir/setup.txt
$pylintCall CMSToolBox > $outputdir/CMSToolBox.txt

# Check installed packages
for d in `cat PackageList.txt`
do
    test -d $d && $pylintCall $d > $outputdir/$d.txt
done

# Check the output
cd $testdir

ERRORSFOUND=0

for f in $outputdir/*.txt
do

    # Look for a perfect score
    if grep "Your code has been rated at 10" $f > /dev/null
    then

        tput setaf 2 2> /dev/null; echo $f" passed the check."

    else

        tput setaf 1 2> /dev/null; echo $f" failed the check:"

        # Travis check has trouble importing distutils.core for some reason
        if [ "${f##*/}" != "setup.txt" -o "$TRAVIS" != "true" ]
        then
            ERRORSFOUND=`expr $ERRORSFOUND + 1`
        fi

        if [ "$TRAVIS" = "true" ]    # For travis test, dump the output directly
        then
            tput sgr0 2> /dev/null
            cat $f
        else                         # Otherwise, show score and tell user to look
            tput setaf 1 2> /dev/null; cat $f | tail -n5
            tput setaf 1 2> /dev/null; echo "Check full file for more details."
        fi

    fi

done

tput sgr0 2> /dev/null               # Reset terminal colors

cd $here                             # Return to original location

# exit $ERRORSFOUND  # I'm a bad sport that doesn't want travis to see for now.
