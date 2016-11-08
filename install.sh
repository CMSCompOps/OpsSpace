#! /bin/bash

# Install the dbs and RestClient packages from dmwm/DBS

if [ ! -d dbs_src ]
then

    git clone --depth=1 https://github.com/dmwm/DBS.git dbs_src
    cd dbs_src || exit 1
    git checkout DBS_3_3_150
    cd .. || exit 1

    mv dbs_src/PycurlClient/src/python/RestClient RestClient
    mv dbs_src/Client/src/python/dbs dbs

    # I don't use this doc at the moment
    rm -rf dbs_src/doc

    # Patch dbsClient for documentation
    patch dbs/apis/dbsClient.py dbsClient.patch

fi
