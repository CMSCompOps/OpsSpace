#!/bin/bash

install=$1

# Check for pylint
if [ "`which pylint 2> /dev/null`" = "" ]
then

    if [ "$install" = "install" -o "$install" = "travis" ]
    then

        pip install pylint

    else

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

# Dump some pylint stores

cd $opsdir

pylintCall="pylint --rcfile docs/pylint.cfg"

$pylintCall setup.py > $outputdir/setup.txt
$pylintCall CMSToolBox > $outputdir/CMSToolBox.txt

for d in `cat PackageList.txt`
do
    test -d $d && $pylintCall $d > $outputdir/$d.txt
done

# Check the output

cd $testdir

for f in $outputdir/*.txt
do

    if grep "Your code has been rated at 10" $f > /dev/null
    then

        tput setaf 2 2> /dev/null; echo $f" passed the check."

    else

        tput setaf 1 2> /dev/null; echo $f" failed the check:"

        if [ "$install" = "travis" ]
        then
            tput sgr0 2> /dev/null
            cat $f
        else
            tput setaf 1 2> /dev/null; cat $f | tail -n5
            tput setaf 1 2> /dev/null; echo "Check full file for more details."
        fi

    fi

done

tput sgr0 2> /dev/null

cd $here
