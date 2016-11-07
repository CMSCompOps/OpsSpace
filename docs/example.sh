#! /bin/bash

##!
# example.sh
# ++++++++++
#
# This is an example script that does nothing or can display help messages.
# The output of::
#
#     ./example.sh -h
#
# is the usage:
#
# .. program-output:: ./example.sh -h
#
# :returns:
#   - 0 - When the script successfully does nothing or has the usage properly called
#   - 1 - When an invalid option is passed
#
# :author: Daniel Abercrombie <dabercro@mit.edu>
##!

usage () {
    echo "Usage: $0 [-h]"
}

while getopts ":h" opt
do
    case "${opt}" in
        h)
            usage
            ;;
        *)
            echo "That's not an option I recognize." 1>&2 
            usage
            exit 1
            ;;
    esac
done

exit 0
