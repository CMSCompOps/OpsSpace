#! /bin/bash

# Check for shellcheck

if [ "$(which shellcheck 2> /dev/null)" = "" ]
then

    if [ "$TRAVIS" = "true" ]
    then

        apt-get install shellcheck

    else

        echo "Please install shellcheck: https://github.com/koalaman/shellcheck" 1>&2
        exit 1

    fi

fi

# Save here, in case user is not in test dir
here=$(pwd)

# Get the test dir
testdir=${0%%$(basename "$0")}
cd "$testdir" || exit 1
testdir=$(pwd)

# Set text output location
outputdir=$testdir"/shellcheck_output"

test -d "$outputdir" || mkdir "$outputdir"

cd ..

ERRORSFOUND=0

# Define the function to check each repository
check_package () {

    location=$(pwd)
    location=${location##*/}

    shellcheck $(git ls-files | grep "\.sh") > "$outputdir/$location.txt"

    if [ $? -eq 0 ]
    then
        return
    fi

    tput setaf 1 2> /dev/null
    echo "$outputdir/$location.txt failed the check."
    tput sgr0 2> /dev/null

    if [ "$TRAVIS" != "true" ] || [ "$location" = "$MUSTWORK" ]
    then

        ERRORSFOUND=$((ERRORSFOUND + 1))

    fi

}

# Check OpsSpace
check_package

# Check each installed package
while read -r package
do

    if [ -d "$package" ]
    then

        cd "$package" || exit 1
        check_package
        cd ..

    fi

done < PackageList.txt

echo "$ERRORSFOUND errors found"

exit "$ERRORSFOUND"
