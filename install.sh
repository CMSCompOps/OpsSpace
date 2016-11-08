#! /bin/bash

# Install the dbs and RestClient packages from dmwm/DBS

if [ ! -d dbs_src ]
then

    git clone https://github.com/dmwm/DBS.git dbs_src

else

    cd dbs_src
    git pull
    cd ..

fi

mv dbs_src/Client/src/python/dbs dbs
mv dbs_src/PycurlClient/src/python/RestClient RestClient
