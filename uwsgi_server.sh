#!/bin/bash

PROJDIR="$(cd -P -- "$(dirname -- "$0")" && pwd -P)"
cd $PROJDIR
source ../aniairadek_env/bin/activate
uwsgi --ini ${PROJDIR}/uwsgi.ini