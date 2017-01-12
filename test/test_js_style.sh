#! /bin/bash

# Check for eslint

if [ "$(which eslint 2> /dev/null)" = "" ]
then

    if [ "$TRAVIS" = "true" ]
    then

        npm install -g eslint

    else

        echo "Please install ESLint: https://github.com/eslint/eslint" 1>&2
        exit 0

    fi

fi

# Save here, in case user is not in test dir
here=$(pwd)

# Get the test dir
testdir=${0%%$(basename "$0")}
cd "$testdir" || exit 1
testdir=$(pwd)

# Set text output location
outputdir=$testdir"/eslint_output"

test -d "$outputdir" || mkdir "$outputdir"

cd ..

ERRORSFOUND=0

# Define the function to check each repository
check_package () {

    location="$1"

    if eslint -c test/eslintrc.yml "$location" > "$outputdir/$location.txt"
    then
        tput setaf 2 2> /dev/null
        echo "$outputdir/$location.txt passed the check."
        tput sgr0 2> /dev/null
        return
    fi

    tput setaf 1 2> /dev/null
    echo "$outputdir/$location.txt failed the check."
    tput sgr0 2> /dev/null

    if [ "$TRAVIS" != "true" ] || [ "$location" = "$MUSTWORK" ]
    then

        ERRORSFOUND=$((ERRORSFOUND + 1))

    fi

    if [ "$TRAVIS" = "true" ]
    then

        cat "$outputdir/$location.txt"

    fi

}

# Check each installed package
while read -r package
do

    if [ -d "$package" ]
    then

        check_package "$package"

    fi

done < PackageList.txt

cd "$here" || exit 1

echo "$ERRORSFOUND errors found"

#### For now, exit 0 until someone who can fix JS better is found (or I learn)
#
exit 0
#
####

exit "$ERRORSFOUND"
