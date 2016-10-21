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

cfg26=test/pylint_py2.6.cfg
cfg27=test/pylint.cfg

if [ $(pylint --version 2> /dev/null | grep pylint | awk '{ print $2 }') = "1.3.1," ]
then

    sed 's/load-plugins=/#/g' $cfg27 > $cfg26
    pylintCall="pylint --rcfile $cfg26"

else

    pylintCall="pylint --rcfile $cfg27"

fi

# Call default OpsSpace tools
$pylintCall setup.py > $outputdir/setup.txt
$pylintCall CMSToolBox > $outputdir/CMSToolBox.txt

# Check installed packages
for d in `cat PackageList.txt`
do

    test -f $d/__init__.py && $pylintCall $d > $outputdir/$d.txt

done

# Clean up Python 2.6 pylint config if it's there
if [ -f $cfg26 ]
then

    rm $cfg26

fi

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

        # pylint does not import distutils from inside a virtualenv
        if [ "$f" = "$outputdir/setup.txt" -a "$OPSFULLTEST" = "true" ]
        then

            tput setaf 1 2> /dev/null
            echo "But it always fails in a virtual environment."
            tput setaf 1 2> /dev/null
            echo "Please run test/test_style.sh separately if you made changes to it."

            if [ "$TRAVIS" != "true" ]    # Allow Travis CI to dump the result just in case,
            then                          #   otherwise, continue onto the next module

                continue

            fi

        fi

        # In continuous integration tests, only check MUSTWORK
        if [ "$TRAVIS" != "true" -o "${MUSTWORK}.txt" = "${f##*/}" ]
        then

            ERRORSFOUND=`expr $ERRORSFOUND + 1`

        fi

        # For travis test, or $install = "dump" dump the output directly
        if [ "$TRAVIS" = "true" -o "$install" = "dump" ]
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

exit $ERRORSFOUND
